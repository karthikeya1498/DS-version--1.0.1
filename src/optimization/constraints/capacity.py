"""Capacity constraint validation."""

from __future__ import annotations

from collections.abc import Sequence

from src.simulation.models import Order, Vehicle


def check_vehicle_capacity(orders: Sequence[Order], vehicle: Vehicle) -> tuple[bool, int, int]:
    """
    Check if total demand of orders respects vehicle capacity.
    Returns: (is_feasible, total_demand, capacity_units)
    """
    total_demand = sum(o.demand_units for o in orders)
    cap = vehicle.capacity_units
    return total_demand <= cap, total_demand, cap
