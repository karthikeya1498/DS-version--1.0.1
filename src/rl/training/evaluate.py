"""Evaluate PPO and a fixed classical baseline on identical scenarios."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.environment.logistics_env import MultiAgentLogisticsEnv


def evaluate(
    episodes: int = 20, seed: int = 42, output: str | Path = "data/processed/phase4/evaluation.json"
) -> dict:
    env = MultiAgentLogisticsEnv(agents=3, zones=5, horizon=24)
    agent = PPOAgent(env.state().observation_dim, env.action_count, PPOConfig(seed=seed))
    agent.train(env, episodes=max(1, episodes))
    ppo_returns, baseline_returns = [], []
    for episode in range(episodes):
        observation = env.reset(seed + 1000 + episode)
        done = False
        ppo_total = 0.0
        baseline_total = 0.0
        while not done:
            action, _, _ = agent.act(observation, deterministic=True)
            joint = np.zeros(env.agents, dtype=int)
            joint[0] = action
            observation, reward, done, _ = env.step(joint)
            ppo_total += reward
        observation = env.reset(seed + 1000 + episode)
        done = False
        while not done:
            observation, reward, done, _ = env.step(np.zeros(env.agents, dtype=int))
            baseline_total += reward
        ppo_returns.append(ppo_total)
        baseline_returns.append(baseline_total)
    result = {
        "algorithm": "ppo_linear_reference",
        "baseline": "all_defer",
        "seed": seed,
        "episodes": episodes,
        "ppo_mean_return": float(np.mean(ppo_returns)),
        "baseline_mean_return": float(np.mean(baseline_returns)),
        "unseen_scenario_seeds": list(range(seed + 1000, seed + 1000 + episodes)),
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
