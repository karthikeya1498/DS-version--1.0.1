"""Fleet vehicle state feature engineering."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from src.simulation.models import Vehicle, VehicleStatus


def extract_vehicle_features(vehicle: Vehicle, current_time: datetime | None = None) -> dict[str, float]:
    """
    Extract state features for a fleet vehicle:
    - capacity utilization
    - remaining capacity
    - shift time remaining
    - availability status
    """
    current_time = current_time or vehicle.available_from
    shift_total_sec = max(1.0, (vehicle.available_until - vehicle.available_from).total_seconds())
    shift_elapsed_sec = max(0.0, (current_time - vehicle.available_from).total_seconds())
    shift_remaining_ratio = max(0.0, min(1.0, 1.0 - (shift_elapsed_sec / shift_total_sec)))

    cap = max(1, vehicle.capacity_units)
    utilization = min(1.0, vehicle.load_units / cap)
    remaining_cap = max(0, vehicle.capacity_units - vehicle.load_units)

    return {
        "capacity_total": float(vehicle.capacity_units),
        "current_load": float(vehicle.load_units),
        "remaining_capacity": float(remaining_cap),
        "capacity_utilization": float(utilization),
        "shift_remaining_ratio": float(shift_remaining_ratio),
        "is_available": float(1.0 if vehicle.status == VehicleStatus.AVAILABLE else 0.0),
    }
