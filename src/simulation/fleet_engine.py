"""Fleet generation and deterministic order dispatch."""

from __future__ import annotations

import random

from src.simulation.models import Location, Order, SimulationConfig, Vehicle, VehicleStatus


class FleetEngine:
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng

    def generate_vehicles(self, locations: list[Location]) -> list[Vehicle]:
        end = self.config.start_time + self.config.duration
        return [
            Vehicle(
                f"vehicle-{i:04d}",
                self.rng.choice(locations),
                self.rng.randint(8, 20),
                self.config.start_time,
                end,
            )
            for i in range(self.config.vehicles)
        ]

    def dispatch(self, order: Order, vehicles: list[Vehicle]) -> tuple[Vehicle | None, float]:
        candidates = [v for v in vehicles if v.can_accept(order.demand_units, order.created_at)]
        if not candidates:
            order.status = order.status.UNAVAILABLE
            return None, 0.0
        vehicle = min(candidates, key=lambda v: (v.load_units, v.vehicle_id))
        vehicle.status = VehicleStatus.BUSY
        vehicle.load_units += order.demand_units
        order.status = order.status.ASSIGNED
        order.assigned_vehicle_id = vehicle.vehicle_id
        return vehicle, self.distance_km(vehicle.current_location, order.destination)

    @staticmethod
    def distance_km(origin: Location, destination: Location) -> float:
        lat_km = (origin.latitude - destination.latitude) * 111.0
        lon_km = (origin.longitude - destination.longitude) * 111.0
        return (lat_km * lat_km + lon_km * lon_km) ** 0.5

    @staticmethod
    def complete_delivery(order: Order, vehicle: Vehicle, delivered_at) -> None:
        order.status = order.status.DELIVERED
        order.delivered_at = delivered_at
        vehicle.status = VehicleStatus.AVAILABLE
        vehicle.load_units = max(0, vehicle.load_units - order.demand_units)
        vehicle.current_location = order.destination
        vehicle.completed_orders += 1
