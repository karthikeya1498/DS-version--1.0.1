"""Objective cost functions and business economic parameter configurations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveConfig:
    """
    Business cost configuration with clear economic units:
    - distance_cost_per_km: $1.00 / km (wear, maintenance, driver base rate)
    - fuel_cost_per_km: $1.50 / km (fuel consumption at fleet average)
    - lateness_cost_per_minute: $5.00 / min (SLA customer penalty)
    - unserved_order_penalty: $50.00 / order (contractual breach / lost revenue)
    - vehicle_activation_cost: $10.00 / vehicle (fixed setup / shift dispatch cost)
    - late_risk_multiplier: $20.00 (expected cost multiplier for predicted risk)
    """

    distance_cost_per_km: float = 1.0
    fuel_cost_per_km: float = 1.5
    lateness_cost_per_minute: float = 5.0
    unserved_order_penalty: float = 50.0
    vehicle_activation_cost: float = 10.0
    late_risk_multiplier: float = 20.0

    def compute_total_cost(
        self,
        distance_km: float,
        lateness_minutes: float = 0.0,
        unserved_orders: int = 0,
        activated_vehicles: int = 0,
        expected_late_risk: float = 0.0,
    ) -> float:
        """Evaluate full economic objective score for a routing plan."""
        return (
            self.distance_cost_per_km * distance_km
            + self.fuel_cost_per_km * distance_km
            + self.lateness_cost_per_minute * lateness_minutes
            + self.unserved_order_penalty * unserved_orders
            + self.vehicle_activation_cost * activated_vehicles
            + self.late_risk_multiplier * expected_late_risk
        )


def total_cost(
    distance: float,
    lateness: float = 0.0,
    fuel: float = 0.0,
    unserved: float = 0.0,
    vehicle_usage: float = 0.0,
    weights: Mapping[str, float] | None = None,
) -> float:
    """Backwards-compatible total cost calculation."""
    w = weights or {
        "distance": 1.0,
        "lateness": 5.0,
        "fuel": 1.5,
        "unserved": 50.0,
        "vehicle_usage": 10.0,
    }
    return (
        w.get("distance", 1.0) * distance
        + w.get("lateness", 5.0) * lateness
        + w.get("fuel", 1.5) * (fuel if fuel > 0 else distance * 1.5)
        + w.get("unserved", 50.0) * unserved
        + w.get("vehicle_usage", 10.0) * vehicle_usage
    )
