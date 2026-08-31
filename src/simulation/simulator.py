"""Deterministic discrete-event logistics simulator with Synthetic and Real-Data Replay modes."""
from __future__ import annotations

from datetime import timedelta
import random
from typing import Callable

from src.simulation.event_engine import EventEngine
from src.simulation.fleet_engine import FleetEngine
from src.simulation.models import (
    EventType,
    OrderStatus,
    SimulationConfig,
    SimulationEvent,
    SimulationMetrics,
    SimulationResult,
    VehicleStatus,
)
from src.simulation.scenario_generator import Scenario, ScenarioGenerator


class LogisticsSimulator:
    """
    Discrete-Event Logistics Simulation Engine.
    Supports Mode A (Synthetic Scenario Generation) and Mode B (Historical / Real-Data Replay).
    """

    def __init__(
        self,
        config: SimulationConfig | None = None,
        custom_scenario: Scenario | None = None,
    ) -> None:
        self.config = config or SimulationConfig()
        self.custom_scenario = custom_scenario
        self.scenario: Scenario | None = None
        self.current_traffic_multipliers: dict[str, float] = {}

    def run(self) -> SimulationResult:
        # Mode A: Synthetic generation, or Mode B: Real-data replay
        if self.custom_scenario is not None:
            self.scenario = self.custom_scenario
        else:
            self.scenario = ScenarioGenerator(self.config).generate()

        fleet = FleetEngine(self.config, random.Random(self.config.seed + 3))
        events = EventEngine()
        distance = 0.0

        # Schedule initial order creations
        for order in self.scenario.orders:
            events.schedule(order.created_at, EventType.ORDER_CREATED, order.order_id)

        # Schedule dynamic traffic updates
        for traffic in self.scenario.traffic_history:
            events.schedule(
                traffic.timestamp,
                EventType.TRAFFIC_UPDATED,
                f"traffic_{traffic.timestamp.isoformat()}",
                {"zone_multipliers": traffic.zone_multipliers},
            )

        # Clean, unified event handler
        def handle_event(event: SimulationEvent) -> None:
            nonlocal distance

            if event.event_type == EventType.ORDER_CREATED:
                order = next((o for o in self.scenario.orders if o.order_id == event.entity_id), None)
                if order is None:
                    return

                vehicle, route_distance = fleet.dispatch(order, self.scenario.vehicles)
                distance += route_distance

                if vehicle is None:
                    order.status = OrderStatus.UNAVAILABLE
                    return

                # Calculate traffic-adjusted travel time
                zone_mult = self.current_traffic_multipliers.get(order.destination.zone_id, 1.0)
                travel_minutes = max(1, round(route_distance * 4.0 * zone_mult))
                delivered_at = event.timestamp + timedelta(minutes=travel_minutes)

                if delivered_at > self.config.start_time + self.config.duration:
                    order.status = OrderStatus.UNAVAILABLE
                    vehicle.status = VehicleStatus.AVAILABLE
                    vehicle.load_units -= order.demand_units
                    return

                order.status = OrderStatus.IN_TRANSIT
                events.schedule(
                    delivered_at,
                    EventType.ORDER_DELIVERED,
                    order.order_id,
                    {"vehicle_id": vehicle.vehicle_id},
                )

            elif event.event_type == EventType.ORDER_DELIVERED:
                order = next((o for o in self.scenario.orders if o.order_id == event.entity_id), None)
                v_id = event.payload.get("vehicle_id") if event.payload else None
                vehicle = next((v for v in self.scenario.vehicles if v.vehicle_id == v_id), None)

                if order and vehicle:
                    fleet.complete_delivery(order, vehicle, event.timestamp)

            elif event.event_type == EventType.TRAFFIC_UPDATED:
                if event.payload and "zone_multipliers" in event.payload:
                    self.current_traffic_multipliers.update(event.payload["zone_multipliers"])

        processed = events.run(handle_event)
        delivered = [o for o in self.scenario.orders if o.status == OrderStatus.DELIVERED]
        late = [o for o in delivered if o.is_late]
        unserved = [o for o in self.scenario.orders if o.status == OrderStatus.UNAVAILABLE]
        cost = distance + len(late) * 5.0 + len(unserved) * 20.0
        end = self.config.start_time + self.config.duration

        return SimulationResult(
            self.config.seed,
            self.config.start_time,
            end,
            self.scenario.orders,
            self.scenario.vehicles,
            processed,
            self.scenario.traffic_history,
            SimulationMetrics(
                len(self.scenario.orders),
                len(delivered),
                len(late),
                len(unserved),
                distance,
                cost,
            ),
        )
