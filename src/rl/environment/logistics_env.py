"""Dependency-light sequential multi-agent logistics environment."""

from __future__ import annotations

from dataclasses import asdict

import numpy as np

from src.rl.environment.action import ACTION_NAMES, Action
from src.rl.environment.reward import RewardWeights, calculate_reward
from src.rl.environment.state import LogisticsState


class MultiAgentLogisticsEnv:
    """Small deterministic environment suitable for PPO and classical baselines."""

    def __init__(
        self,
        agents: int = 3,
        zones: int = 5,
        horizon: int = 24,
        demand_rate: float = 2.0,
        reward_weights: RewardWeights | None = None,
    ):
        if min(agents, zones, horizon) <= 0:
            raise ValueError("agents, zones, and horizon must be positive")
        self.agents, self.zones, self.horizon, self.demand_rate = (
            agents,
            zones,
            horizon,
            demand_rate,
        )
        self.reward_weights = reward_weights or RewardWeights(reward_scale=50.0, reward_clip=10.0)
        self.action_count = len(Action)
        self.rng = np.random.default_rng(42)
        self.reset(42)

    def reset(self, seed: int | None = None) -> np.ndarray:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.time_step = 0
        self.pending = np.zeros(self.zones, dtype=np.float32)
        self.positions = np.zeros(self.agents, dtype=np.float32)
        self.capacity = np.ones(self.agents, dtype=np.float32)
        self.traffic = np.ones(self.zones, dtype=np.float32)
        self.total_served = 0
        self.total_cost = 0.0
        self.pending += self.rng.poisson(self.demand_rate, self.zones).astype(np.float32)
        return self.state().vector()

    def state(self) -> LogisticsState:
        return LogisticsState(
            self.time_step,
            self.pending.copy(),
            self.positions.copy(),
            self.capacity.copy(),
            self.traffic.copy(),
        )

    def action_mask(self) -> np.ndarray:
        mask = np.ones((self.agents, self.action_count), dtype=bool)
        mask[:, Action.SERVE] = self.pending.sum() > 0
        mask[:, Action.REROUTE] = self.traffic.mean() > 1.0
        mask[:, Action.REPOSITION] = self.capacity < 1.0
        return mask

    def step(self, actions: list[int] | np.ndarray) -> tuple[np.ndarray, float, bool, dict]:
        actions = np.asarray(actions, dtype=int).reshape(-1)
        if actions.size != self.agents:
            raise ValueError(f"expected {self.agents} actions")
        before = self.pending.sum()
        served = 0
        operating_cost = 0.0
        completed_priority = 0
        for agent, action in enumerate(actions):
            if action not in ACTION_NAMES:
                raise ValueError(f"unknown action: {action}")
            if action == Action.SERVE and self.pending.sum() > 0:
                zone = int(np.argmax(self.pending))
                amount = min(1.0, self.pending[zone])
                self.pending[zone] -= amount
                self.capacity[agent] = max(0.0, self.capacity[agent] - amount)
                self.positions[agent] = zone
                served += int(amount)
                completed_priority += int(zone == 0)
                operating_cost += 1.0 * self.traffic[zone]
            elif action == Action.REROUTE:
                operating_cost += 0.5 * self.traffic.mean()
                self.traffic = np.maximum(1.0, self.traffic * 0.98)
            elif action == Action.REPOSITION:
                operating_cost += 0.25
                self.capacity[agent] = min(1.0, self.capacity[agent] + 0.5)
            else:
                operating_cost += 0.1
        arrivals = self.rng.poisson(self.demand_rate, self.zones).astype(np.float32)
        self.pending += arrivals
        self.traffic = np.clip(self.traffic + self.rng.normal(0, 0.04, self.zones), 0.75, 1.6)
        self.time_step += 1
        unserved = int(max(0.0, self.pending.sum() - before))
        breakdown = calculate_reward(
            operating_cost=operating_cost,
            late_orders=int(unserved > 0),
            unserved_orders=unserved,
            completed_priority=completed_priority,
            weights=self.reward_weights,
        )
        self.total_served += served
        self.total_cost += operating_cost
        done = self.time_step >= self.horizon
        info = {
            "actions": [ACTION_NAMES[int(action)] for action in actions],
            "served": served,
            "arrivals": int(arrivals.sum()),
            "pending": int(self.pending.sum()),
            "reward_breakdown": asdict(breakdown),
            "action_mask": self.action_mask().tolist(),
        }
        return self.state().vector(), float(breakdown.total), done, info


LogisticsEnv = MultiAgentLogisticsEnv
