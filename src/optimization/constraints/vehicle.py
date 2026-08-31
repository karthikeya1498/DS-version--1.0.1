"""Vehicle shift and availability constraints."""

from __future__ import annotations

from datetime import datetime

from src.simulation.models import Vehicle, VehicleStatus


def check_vehicle_availability(
    vehicle: Vehicle,
    timestamp: datetime | None = None,
) -> tuple[bool, str | None]:
    """Check if vehicle is available and within active shift hours."""
    if vehicle.status != VehicleStatus.AVAILABLE:
        return False, f"vehicle_not_available:{vehicle.vehicle_id}"

    if timestamp is not None:
        if not (vehicle.available_from <= timestamp <= vehicle.available_until):
            return False, f"vehicle_out_of_shift:{vehicle.vehicle_id}"

    return True, None
