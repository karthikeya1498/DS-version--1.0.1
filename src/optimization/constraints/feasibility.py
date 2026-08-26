"""Hard feasibility checks for single-vehicle routes."""

from dataclasses import dataclass
from datetime import timedelta

from src.simulation.models import Order, Vehicle


@dataclass(frozen=True)
class FeasibilityResult:
    feasible: bool
    violations: tuple[str, ...]


def validate_route(
    route: list[Order], vehicle: Vehicle, start_time, travel_minutes: dict[tuple[str, str], float]
) -> FeasibilityResult:
    violations, load, current, timestamp = [], 0, vehicle.current_location.node_id, start_time
    if not vehicle.available_from <= start_time <= vehicle.available_until:
        violations.append("vehicle_unavailable_at_start")
    for order in route:
        load += order.demand_units
        if load > vehicle.capacity_units:
            violations.append(f"capacity_exceeded:{order.order_id}")
        key = (current, order.destination.node_id)
        if key not in travel_minutes:
            violations.append(f"route_missing:{current}->{order.destination.node_id}")
            continue
        timestamp += timedelta(minutes=travel_minutes[key])
        timestamp = max(timestamp, order.time_window.start)
        if timestamp > order.time_window.end:
            violations.append(f"time_window_missed:{order.order_id}")
        current = order.destination.node_id
    if timestamp > vehicle.available_until:
        violations.append("vehicle_shift_exceeded")
    return FeasibilityResult(not violations, tuple(violations))
