"""Run the Phase 4 PPO training and unseen-scenario evaluation workflow."""
from __future__ import annotations

import json
from pathlib import Path

from src.rl.training.evaluate import evaluate
from src.rl.training.train import train


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    training = train(episodes=100, seed=42, output=root / 'data/processed/phase4/ppo_training.json')
    evaluation = evaluate(episodes=20, seed=42, output=root / 'data/processed/phase4/evaluation.json')
    summary = {'training': training, 'evaluation': evaluation, 'environment': {'agents': 3, 'zones': 5, 'horizon': 24, 'action_space': ['defer', 'serve', 'reroute', 'reposition']}}
    (root / 'data/processed/phase4/summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'training_mean_return': training['mean_return'], 'ppo_mean_return': evaluation['ppo_mean_return'], 'baseline_mean_return': evaluation['baseline_mean_return']}, indent=2))

if __name__ == '__main__': main()
