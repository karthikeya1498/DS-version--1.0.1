"""Reward shaping with auditable operational components."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RewardWeights:
    operating_cost: float = 1.0
    lateness: float = 5.0
    unserved: float = 10.0
    priority_completion: float = 2.0
    reward_scale: float = 1.0
    reward_clip: float | None = None

@dataclass(frozen=True)
class RewardBreakdown:
    operating_cost: float
    lateness: float
    unserved: float
    priority_completion: float

    @property
    def total(self) -> float:
        return self.operating_cost + self.lateness + self.unserved + self.priority_completion

def calculate_reward(*, operating_cost: float, late_orders: int, unserved_orders: int, completed_priority: int, weights: RewardWeights = RewardWeights()) -> RewardBreakdown:
    raw = RewardBreakdown(-weights.operating_cost * operating_cost, -weights.lateness * late_orders, -weights.unserved * unserved_orders, weights.priority_completion * completed_priority)
    scale = max(weights.reward_scale, 1e-9)
    values = tuple(component / scale for component in (raw.operating_cost, raw.lateness, raw.unserved, raw.priority_completion))
    if weights.reward_clip is not None:
        limit = abs(weights.reward_clip); values = tuple(max(-limit, min(limit, component)) for component in values)
    return RewardBreakdown(*values)
