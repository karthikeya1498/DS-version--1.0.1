"""Train PPO on the sequential logistics environment."""
from __future__ import annotations

import json
from pathlib import Path

from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.environment.logistics_env import MultiAgentLogisticsEnv


def train(episodes: int = 100, seed: int = 42, output: str | Path = 'data/processed/phase4/ppo_training.json') -> dict:
    env = MultiAgentLogisticsEnv(agents=3, zones=5, horizon=24)
    agent = PPOAgent(env.state().observation_dim, env.action_count, PPOConfig(seed=seed))
    metrics = agent.train(env, episodes=episodes)
    result = {'algorithm': 'ppo_linear_reference', 'seed': seed, 'episodes': episodes, 'mean_return': metrics.mean_return, 'final_return': metrics.final_return, 'returns': metrics.returns, 'policy_losses': metrics.policy_losses, 'value_losses': metrics.value_losses}
    path = Path(output); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result

if __name__ == '__main__': print(json.dumps(train(), indent=2))
