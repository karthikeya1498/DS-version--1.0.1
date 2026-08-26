"""Synthetic demand generation with deterministic seeded randomness."""

from __future__ import annotations

import random
from datetime import timedelta

from src.simulation.models import Location, Order, SimulationConfig, TimeWindow


class DemandEngine:
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng

    def generate_locations(self) -> list[Location]:
        count = max(self.config.zones, 2)
        return [
            Location(
                f"node-{i}", f"zone-{i % self.config.zones}", 12.9 + i * 0.001, 77.5 + i * 0.001
            )
            for i in range(count)
        ]

    def generate_orders(self, locations: list[Location]) -> list[Order]:
        orders: list[Order] = []
        interval_minutes = 60 / self.config.orders_per_hour
        total = round(self.config.orders_per_hour * self.config.duration.total_seconds() / 3600)
        for index in range(total):
            created_at = self.config.start_time + timedelta(minutes=index * interval_minutes)
            origin = self.rng.choice(locations)
            destination = self.rng.choice([loc for loc in locations if loc != origin])
            window_start = created_at + timedelta(minutes=self.rng.randint(5, 30))
            window = TimeWindow(
                window_start, window_start + timedelta(minutes=self.rng.randint(30, 90))
            )
            orders.append(
                Order(
                    f"order-{index:05d}",
                    origin,
                    destination,
                    self.rng.randint(1, self.config.max_order_demand),
                    created_at,
                    window,
                    self.rng.randint(1, 3),
                )
            )
        return orders
