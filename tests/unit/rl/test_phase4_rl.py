import numpy as np

from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.environment.action import Action
from src.rl.environment.logistics_env import MultiAgentLogisticsEnv
from src.rl.environment.reward import RewardWeights, calculate_reward


def test_environment_is_reproducible_and_multi_agent():
    first = MultiAgentLogisticsEnv(agents=2, zones=3, horizon=4)
    second = MultiAgentLogisticsEnv(agents=2, zones=3, horizon=4)
    obs_a, obs_b = first.reset(7), second.reset(7)
    assert np.array_equal(obs_a, obs_b)
    next_a = first.step([Action.SERVE, Action.DEFER])
    next_b = second.step([Action.SERVE, Action.DEFER])
    assert np.array_equal(next_a[0], next_b[0]) and next_a[1] == next_b[1]
    assert next_a[3]['actions'] == ['serve', 'defer']


def test_action_mask_and_reward_decomposition():
    env = MultiAgentLogisticsEnv(agents=2, zones=2, horizon=2)
    env.reset(11)
    mask = env.action_mask()
    assert mask.shape == (2, 4)
    breakdown = calculate_reward(operating_cost=2, late_orders=1, unserved_orders=3, completed_priority=2, weights=RewardWeights())
    assert breakdown.total == -33


def test_ppo_trains_and_returns_metrics():
    env = MultiAgentLogisticsEnv(agents=2, zones=3, horizon=5)
    agent = PPOAgent(env.state().observation_dim, env.action_count, PPOConfig(seed=3, epochs=2))
    metrics = agent.train(env, episodes=4)
    assert metrics.episodes == 4
    assert len(metrics.returns) == 4
    assert np.isfinite(metrics.mean_return)
    action, log_prob, value = agent.act(env.reset(4), deterministic=True)
    assert 0 <= action < env.action_count
    assert np.isfinite(log_prob) and np.isfinite(value)
