"""Deterministic nearest-feasible-order route construction and sequence optimization."""
from __future__ import annotations

from typing import Callable, Sequence

from src.optimization.constraints.feasibility import validate_route
from src.simulation.models import Order, Vehicle


def construct_route(
    orders: list[Order],
    vehicle: Vehicle,
    start_time,
    travel_minutes: dict[tuple[str, str], float],
) -> list[Order]:
    remaining, route = list(orders), []
    while remaining:
        candidates = []
        for order in remaining:
            candidate = route + [order]
            check = validate_route(candidate, vehicle, start_time, travel_minutes)
            if check.feasible:
                previous = (
                    vehicle.current_location.node_id if not route else route[-1].destination.node_id
                )
                candidates.append(
                    (
                        travel_minutes.get((previous, order.destination.node_id), float("inf")),
                        -order.priority,
                        order.order_id,
                        order,
                    )
                )
        if not candidates:
            break
        chosen = min(candidates, key=lambda item: item[:3])[3]
        route.append(chosen)
        remaining.remove(chosen)
    return route


def optimize(sequence: Sequence[str], cost_fn: Callable[[list[str]], float]) -> tuple[list[str], float]:
    """Identity greedy sequence optimization baseline."""
    seq = list(sequence)
    return seq, cost_fn(seq)
