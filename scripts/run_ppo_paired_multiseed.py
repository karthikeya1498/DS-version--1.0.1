"""Evaluate PPO seeds on one shared set of scenarios to isolate policy variance."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.environment.logistics_env import MultiAgentLogisticsEnv


def evaluate_agent(agent: PPOAgent, scenario_seeds: list[int], horizon: int) -> tuple[list[float], list[float]]:
    ppo_returns, baseline_returns = [], []
    for scenario_seed in scenario_seeds:
        env = MultiAgentLogisticsEnv(agents=3, zones=5, horizon=horizon)
        observation = env.reset(scenario_seed); done = False; ppo_total = 0.0
        while not done:
            action, _, _ = agent.act(observation, deterministic=True); joint = np.zeros(env.agents, dtype=int); joint[0] = action; observation, reward, done, _ = env.step(joint); ppo_total += reward
        observation = env.reset(scenario_seed); done = False; baseline_total = 0.0
        while not done:
            observation, reward, done, _ = env.step(np.zeros(env.agents, dtype=int)); baseline_total += reward
        ppo_returns.append(ppo_total); baseline_returns.append(baseline_total)
    return ppo_returns, baseline_returns


def main() -> None:
    root = Path(__file__).resolve().parents[1]; output = root / 'data/processed/phase4/ppo_paired_multiseed'; output.mkdir(parents=True, exist_ok=True)
    train_seeds, scenario_seeds, horizon = [7, 21, 42, 84, 123], list(range(2000, 2020)), 12
    rows = []
    for train_seed in train_seeds:
        env = MultiAgentLogisticsEnv(agents=3, zones=5, horizon=horizon); agent = PPOAgent(env.state().observation_dim, env.action_count, PPOConfig(learning_rate=0.005, seed=train_seed)); agent.train(env, episodes=60)
        ppo, baseline = evaluate_agent(agent, scenario_seeds, horizon); rows.append({'train_seed': train_seed, 'scenario_seeds': scenario_seeds, 'ppo_returns': ppo, 'baseline_returns': baseline, 'ppo_mean_return': float(np.mean(ppo)), 'baseline_mean_return': float(np.mean(baseline)), 'delta_mean_return': float(np.mean(np.asarray(ppo) - np.asarray(baseline))), 'delta_std_return': float(np.std(np.asarray(ppo) - np.asarray(baseline), ddof=1))})
    deltas = np.asarray([row['delta_mean_return'] for row in rows]); summary = {'configuration': {'learning_rate': 0.005, 'horizon': horizon, 'train_episodes': 60, 'evaluation_scenarios': len(scenario_seeds)}, 'train_seeds': train_seeds, 'scenario_seeds': scenario_seeds, 'runs': rows, 'mean_delta_across_policies': float(deltas.mean()), 'std_delta_across_policies': float(deltas.std(ddof=1)), 'policy_wins': int((deltas > 0).sum()), 'policy_win_rate': float((deltas > 0).mean())}
    (output / 'results.json').write_text(json.dumps(summary, indent=2), encoding='utf-8'); print(json.dumps({key: summary[key] for key in ('mean_delta_across_policies', 'std_delta_across_policies', 'policy_wins', 'policy_win_rate')}, indent=2))


if __name__ == '__main__':
    main()
