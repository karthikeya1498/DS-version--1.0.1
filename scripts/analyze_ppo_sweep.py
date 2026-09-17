"""Summarize PPO sweep results and loss stability."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parents[1]; folder = root / 'data/processed/phase4/ppo_sweep'; rows = json.loads((folder / 'results.json').read_text(encoding='utf-8'))
    ranked = sorted(rows, key=lambda row: row['ppo_mean_return'], reverse=True)
    lines = ['# PPO sweep analysis', '', '| Learning rate | Horizon | PPO mean return | Baseline mean return | Delta vs baseline | Return SD | Policy loss SD | Value loss SD |', '|---:|---:|---:|---:|---:|---:|---:|---:|']
    for row in ranked:
        delta = row['ppo_mean_return'] - row['baseline_mean_return']; policy_sd = float(np.std(row['policy_losses'])); value_sd = float(np.std(row['value_losses']))
        lines.append(f"| {row['learning_rate']:.3f} | {row['horizon']} | {row['ppo_mean_return']:.3f} | {row['baseline_mean_return']:.3f} | {delta:.3f} | {row['ppo_std_return']:.3f} | {policy_sd:.4f} | {value_sd:.3f} |")
    best = ranked[0]; lines += ['', f"Best configuration by mean return: learning rate **{best['learning_rate']}**, horizon **{best['horizon']}**, PPO return **{best['ppo_mean_return']:.3f}**, baseline **{best['baseline_mean_return']:.3f}**, delta **{best['ppo_mean_return'] - best['baseline_mean_return']:.3f}**.", '', 'Interpretation: higher return is better because rewards are negative costs. Losses are diagnostics; business return and the delta against the identical baseline determine whether a configuration is useful.']
    (folder / 'analysis.md').write_text('\n'.join(lines) + '\n', encoding='utf-8'); print('\n'.join(lines))

if __name__ == '__main__': main()
