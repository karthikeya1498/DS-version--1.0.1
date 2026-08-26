"""Reproducible scenario factory."""

from __future__ import annotations

import random

from src.simulation.demand_engine import DemandEngine
from src.simulation.fleet_engine import FleetEngine
from src.simulation.models import Order, SimulationConfig, Vehicle
from src.simulation.traffic_engine import TrafficEngine


class Scenario:
    def __init__(
        self,
        config: SimulationConfig,
        orders: list[Order],
        vehicles: list[Vehicle],
        traffic_history: list,
    ) -> None:
        self.config, self.orders, self.vehicles, self.traffic_history = (
            config,
            orders,
            vehicles,
            traffic_history,
        )


class ScenarioGenerator:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def generate(self) -> Scenario:
        demand_rng = random.Random(self.config.seed + 1)
        traffic_rng = random.Random(self.config.seed + 2)
        fleet_rng = random.Random(self.config.seed + 3)
        demand = DemandEngine(self.config, demand_rng)
        locations = demand.generate_locations()
        return Scenario(
            self.config,
            demand.generate_orders(locations),
            FleetEngine(self.config, fleet_rng).generate_vehicles(locations),
            TrafficEngine(self.config, traffic_rng).generate_history(),
        )
