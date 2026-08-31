"""Analyze sources of variance in the five-seed PPO validation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    folder = root / "data/processed/phase4/ppo_multiseed"
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    rows = summary["runs"]
    for row in rows:
        row["delta_vs_baseline"] = row["ppo_mean_return"] - row["baseline_mean_return"]
        row["policy_loss_sd"] = float(np.std(row["policy_losses"], ddof=1))
        row["value_loss_sd"] = float(np.std(row["value_losses"], ddof=1))
    ppo = np.array([row["ppo_mean_return"] for row in rows])
    baseline = np.array([row["baseline_mean_return"] for row in rows])
    delta = np.array([row["delta_vs_baseline"] for row in rows])
    report = {
        "seed_rows": [
            {
                key: row[key]
                for key in (
                    "seed",
                    "ppo_mean_return",
                    "baseline_mean_return",
                    "delta_vs_baseline",
                    "ppo_std_return",
                    "policy_loss_sd",
                    "value_loss_sd",
                )
            }
            for row in rows
        ],
        "ppo_return_range": float(ppo.max() - ppo.min()),
        "baseline_return_range": float(baseline.max() - baseline.min()),
        "delta_range": float(delta.max() - delta.min()),
        "ppo_baseline_return_correlation": float(np.corrcoef(ppo, baseline)[0, 1]),
        "delta_mean": float(delta.mean()),
        "delta_std": float(delta.std(ddof=1)),
        "best_seed": int(rows[int(np.argmax(delta))]["seed"]),
        "worst_seed": int(rows[int(np.argmin(delta))]["seed"]),
        "diagnosis": [
            "The environment is stochastic during training because reset and every step draw Poisson demand and Gaussian traffic noise from the seeded RNG.",
            "The policy is stochastic during training because PPO samples actions; deterministic inference removes action-sampling variance from evaluation.",
            "The baseline changes by seed because each seed evaluates different unseen scenario seeds, so part of the variance is scenario difficulty rather than policy quality.",
            "The short horizon leaves little temporal credit-assignment signal, and the linear policy/value heads are low-capacity for the unnormalized operational structure.",
            "The value loss is frequently clipped at 100 and the policy loss is noisy, indicating bounded but unstable updates rather than smooth convergence.",
        ],
    }
    (folder / "variance_analysis.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
