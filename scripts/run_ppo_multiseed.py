"""Validate the selected PPO hyperparameters across independent random seeds."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from run_ppo_sweep import run_case


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / 'data/processed/phase4/ppo_multiseed'
    output.mkdir(parents=True, exist_ok=True)
    seeds = [7, 21, 42, 84, 123]
    rows = [run_case(learning_rate=0.005, horizon=12, seed=seed, train_episodes=60, eval_episodes=20) for seed in seeds]
    ppo = np.asarray([row['ppo_mean_return'] for row in rows])
    baseline = np.asarray([row['baseline_mean_return'] for row in rows])
    deltas = ppo - baseline
    summary = {
        'configuration': {'learning_rate': 0.005, 'horizon': 12, 'train_episodes': 60, 'eval_episodes': 20},
        'seeds': seeds,
        'runs': rows,
        'ppo_mean_return': float(ppo.mean()),
        'ppo_std_return': float(ppo.std(ddof=1)),
        'baseline_mean_return': float(baseline.mean()),
        'baseline_std_return': float(baseline.std(ddof=1)),
        'delta_mean_return': float(deltas.mean()),
        'delta_std_return': float(deltas.std(ddof=1)),
        'wins_against_baseline': int((deltas > 0).sum()),
        'win_rate': float((deltas > 0).mean()),
    }
    (output / 'runs.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    (output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key not in {'configuration', 'seeds', 'runs'}}, indent=2))


if __name__ == '__main__':
    main()
