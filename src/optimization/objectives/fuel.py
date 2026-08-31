"""Fuel consumption and emission objective calculations."""
from __future__ import annotations


def calculate_fuel_cost(distance_km: float, fuel_rate_per_km: float = 1.5) -> float:
    return distance_km * fuel_rate_per_km
