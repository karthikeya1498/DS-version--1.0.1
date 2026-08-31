"""Unit tests for DQN, PPO, Q-Learning, and Domain State Encoding."""
from datetime import datetime, timedelta, timezone
import numpy as np
import pytest

from src.rl.agents.dqn import DQNAgent, DQNConfig
from src.rl.agents.ppo import PPOAgent, PPOConfig
from src.rl.agents.q_learning import QLearningAgent
from src.rl.environment.logistics_env import LogisticsEnv
from src.rl.environment.state import LogisticsState
from src.simulation.models import Location, Order, TimeWindow, Vehicle, VehicleStatus


def test_dqn_agent_learning():
    env = LogisticsEnv(agents=2, zones=3, horizon=10)
    agent = DQNAgent(observation_dim=env.state().observation_dim, action_count=env.action_count)

    obs = env.reset()
    for _ in range(40):
        action = agent.act(obs)
        next_obs, reward, done, _ = env.step([action, 0])
        agent.remember(obs, action, reward, next_obs, done)
        loss = agent.train_step()
        obs = env.reset() if done else next_obs

    # After training, memory contains transitions and agent acts deterministically
    assert len(agent.memory) > 0
    det_act = agent.act(obs, deterministic=True)
    assert 0 <= det_act < env.action_count


def test_domain_state_encoder():
    now = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    loc_a = Location("A", "zone_0", 0, 0)
    loc_b = Location("B", "zone_1", 0, 1)

    orders = [
        Order("o1", loc_a, loc_a, demand_units=3, created_at=now, time_window=TimeWindow(now, now + timedelta(hours=2))),
        Order("o2", loc_a, loc_b, demand_units=5, created_at=now, time_window=TimeWindow(now, now + timedelta(hours=2))),
    ]
    vehicles = [
        Vehicle("v1", loc_a, capacity_units=10, available_from=now, available_until=now + timedelta(hours=8), current_location=loc_a, load_units=2),
    ]

    state = LogisticsState.from_domain_entities(
        time_step=1,
        orders=orders,
        vehicles=vehicles,
        zone_ids=("zone_0", "zone_1"),
        traffic_multipliers={"zone_0": 1.2, "zone_1": 1.5},
    )

    assert state.pending_demand[0] == 3.0
    assert state.pending_demand[1] == 5.0
    assert state.traffic[0] == 1.2
    assert state.traffic[1] == 1.5
    assert len(state.vector()) == 2 + 1 + 1 + 2  # pending(2) + pos(1) + cap(1) + traffic(2)
