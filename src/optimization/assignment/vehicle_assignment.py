"""Vehicle fleet allocation and insertion optimizer."""
from __future__ import annotations

from typing import Sequence

from src.optimization.assignment.order_assignment import cluster_orders_by_capacity
from src.simulation.models import Order, Vehicle


class VehicleAssignmentSolver:
    """Assigns order subsets to fleet vehicles considering capacity and location."""

    def __init__(self) -> None:
        pass

    def assign(
        self,
        orders: Sequence[Order],
        vehicles: Sequence[Vehicle],
    ) -> tuple[dict[str, list[Order]], list[Order]]:
        return cluster_orders_by_capacity(orders, vehicles)
