"""Sweep PPO learning rates and horizons on identical seeded evaluation scenarios."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.environment.logistics_env import MultiAgentLogisticsEnv


def run_case(
    learning_rate: float,
    horizon: int,
    seed: int = 42,
    train_episodes: int = 40,
    eval_episodes: int = 12,
) -> dict:
    env = MultiAgentLogisticsEnv(agents=3, zones=5, horizon=horizon)
    agent = PPOAgent(
        env.state().observation_dim,
        env.action_count,
        PPOConfig(learning_rate=learning_rate, seed=seed),
    )
    metrics = agent.train(env, train_episodes)
    ppo_returns, baseline_returns = [], []
    for offset in range(eval_episodes):
        observation = env.reset(seed + 1000 + offset)
        done = False
        ppo_total = 0.0
        while not done:
            action, _, _ = agent.act(observation, deterministic=True)
            joint = np.zeros(env.agents, dtype=int)
            joint[0] = action
            observation, reward, done, _ = env.step(joint)
            ppo_total += reward
        observation = env.reset(seed + 1000 + offset)
        done = False
        baseline_total = 0.0
        while not done:
            observation, reward, done, _ = env.step(np.zeros(env.agents, dtype=int))
            baseline_total += reward
        ppo_returns.append(ppo_total)
        baseline_returns.append(baseline_total)
    return {
        "learning_rate": learning_rate,
        "horizon": horizon,
        "seed": seed,
        "train_episodes": train_episodes,
        "eval_episodes": eval_episodes,
        "train_mean_return": metrics.mean_return,
        "ppo_mean_return": float(np.mean(ppo_returns)),
        "ppo_std_return": float(np.std(ppo_returns)),
        "baseline_mean_return": float(np.mean(baseline_returns)),
        "policy_losses": list(metrics.policy_losses),
        "value_losses": list(metrics.value_losses),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "data/processed/phase4/ppo_sweep"
    output.mkdir(parents=True, exist_ok=True)
    results = [run_case(rate, horizon) for rate in (0.005, 0.02, 0.05) for horizon in (12, 24, 48)]
    (output / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    best = max(results, key=lambda row: row["ppo_mean_return"])
    plt.figure(figsize=(9, 5))
    for row in results:
        plt.plot(row["policy_losses"], label=f"lr={row['learning_rate']}, H={row['horizon']}")
    plt.xlabel("Training episode")
    plt.ylabel("Policy loss")
    plt.title("PPO policy-loss curves")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output / "policy_loss_curves.png", dpi=160)
    plt.close()
    plt.figure(figsize=(9, 5))
    for row in results:
        plt.plot(row["value_losses"], label=f"lr={row['learning_rate']}, H={row['horizon']}")
    plt.xlabel("Training episode")
    plt.ylabel("Value loss")
    plt.title("PPO value-loss curves")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output / "value_loss_curves.png", dpi=160)
    plt.close()
    summary = {
        "cases": len(results),
        "best_by_ppo_return": best,
        "learning_rates": [0.005, 0.02, 0.05],
        "horizons": [12, 24, 48],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "cases": len(results),
                "best_learning_rate": best["learning_rate"],
                "best_horizon": best["horizon"],
                "best_ppo_mean_return": best["ppo_mean_return"],
                "best_baseline_mean_return": best["baseline_mean_return"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
