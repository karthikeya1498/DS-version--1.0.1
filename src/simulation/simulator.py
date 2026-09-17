"""Deterministic discrete-event logistics simulator."""

from __future__ import annotations

from datetime import timedelta

from src.simulation.event_engine import EventEngine
from src.simulation.fleet_engine import FleetEngine
from src.simulation.models import (
    EventType,
    OrderStatus,
    SimulationConfig,
    SimulationEvent,
    SimulationMetrics,
    SimulationResult,
)
from src.simulation.scenario_generator import Scenario, ScenarioGenerator


class LogisticsSimulator:
    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        self.scenario: Scenario | None = None

    def run(self) -> SimulationResult:
        self.scenario = ScenarioGenerator(self.config).generate()
        fleet = FleetEngine(self.config, __import__("random").Random(self.config.seed + 3))
        events = EventEngine()
        distance = 0.0
        for order in self.scenario.orders:
            events.schedule(order.created_at, EventType.ORDER_CREATED, order.order_id)
        for traffic in self.scenario.traffic_history:
            events.schedule(
                traffic.timestamp, EventType.TRAFFIC_UPDATED, traffic.timestamp.isoformat()
            )

        def handle(event: SimulationEvent) -> None:
            nonlocal distance
            if event.event_type != EventType.ORDER_CREATED:
                return
            order = next(o for o in self.scenario.orders if o.order_id == event.entity_id)
            vehicle, route_distance = fleet.dispatch(order, self.scenario.vehicles)
            distance += route_distance
            if vehicle is None:
                return
            travel_minutes = max(1, round(route_distance * 4))
            delivered_at = order.created_at + timedelta(minutes=travel_minutes)
            if delivered_at > self.config.start_time + self.config.duration:
                order.status = OrderStatus.UNAVAILABLE
                return
            events.schedule(
                delivered_at,
                EventType.ORDER_DELIVERED,
                order.order_id,
                {"vehicle_id": vehicle.vehicle_id},
            )
            if order.status == OrderStatus.ASSIGNED:
                order.status = OrderStatus.IN_TRANSIT
            elif event.event_type == EventType.ORDER_DELIVERED:
                fleet.complete_delivery(order, vehicle, delivered_at)

        # Delivery events need explicit handling after creation events.
        def handle_event(event: SimulationEvent) -> None:
            if event.event_type == EventType.ORDER_CREATED:
                handle(event)
            elif event.event_type == EventType.ORDER_DELIVERED:
                order = next(o for o in self.scenario.orders if o.order_id == event.entity_id)
                vehicle = next(
                    v for v in self.scenario.vehicles if v.vehicle_id == event.payload["vehicle_id"]
                )
                fleet.complete_delivery(order, vehicle, event.timestamp)

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
                len(self.scenario.orders), len(delivered), len(late), len(unserved), distance, cost
            ),
        )
