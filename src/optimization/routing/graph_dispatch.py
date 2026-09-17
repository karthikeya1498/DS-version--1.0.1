"""Capacity-aware fleet dispatch using traffic-aware shortest paths."""

from __future__ import annotations

from dataclasses import dataclass

from src.dsa.graphs.astar import shortest_path as astar
from src.dsa.graphs.dijkstra import shortest_path as dijkstra
from src.dsa.graphs.graph import RoadGraph
from src.simulation.fleet_engine import FleetEngine
from src.simulation.models import Order, Vehicle, VehicleStatus


@dataclass(frozen=True)
class DispatchRoute:
    vehicle_id: str
    order_id: str
    path: tuple[str, ...]
    travel_cost: float
    algorithm: str


class GraphDispatchRouter:
    def __init__(self, graph: RoadGraph, algorithm: str = "astar") -> None:
        if algorithm not in {"astar", "dijkstra"}:
            raise ValueError("algorithm must be 'astar' or 'dijkstra'")
        self.graph, self.algorithm = graph, algorithm

    def route(self, order: Order, vehicles: list[Vehicle], timestamp=None) -> DispatchRoute | None:
        timestamp = timestamp or order.created_at
        candidates = [
            v
            for v in vehicles
            if v.can_accept(order.demand_units, timestamp)
            and v.current_location.node_id in self.graph.nodes
        ]
        routes = []
        solver = astar if self.algorithm == "astar" else dijkstra
        for vehicle in candidates:
            result = solver(self.graph, vehicle.current_location.node_id, order.destination.node_id)
            if result is not None:
                routes.append((result.cost, vehicle.vehicle_id, vehicle, result))
        if not routes:
            return None
        cost, _, vehicle, result = min(routes, key=lambda item: (item[0], item[1]))
        vehicle.status = VehicleStatus.BUSY
        vehicle.load_units += order.demand_units
        order.status = order.status.IN_TRANSIT
        order.assigned_vehicle_id = vehicle.vehicle_id
        return DispatchRoute(vehicle.vehicle_id, order.order_id, result.path, cost, self.algorithm)

    def route_batch(
        self, orders: list[Order], vehicles: list[Vehicle], timestamp=None
    ) -> list[DispatchRoute]:
        """Assign a batch across multiple stops without stopping after one order.

        The reservation map is deliberately separate from ``Vehicle.status``. A vehicle
        becomes busy after its first stop, but can still receive later stops in the same
        atomic planning batch until its capacity is exhausted.
        """
        timestamp = timestamp or (orders[0].created_at if orders else None)
        if timestamp is None:
            return []
        reserved = {vehicle.vehicle_id: vehicle.load_units for vehicle in vehicles}
        cursors = {vehicle.vehicle_id: vehicle.current_location for vehicle in vehicles}
        routes: list[DispatchRoute] = []
        solver = astar if self.algorithm == "astar" else dijkstra
        ordered = sorted(orders, key=lambda item: (-item.priority, item.created_at, item.order_id))
        for order in ordered:
            candidates = []
            for vehicle in vehicles:
                cursor = cursors[vehicle.vehicle_id]
                if cursor is None or cursor.node_id not in self.graph.nodes:
                    continue
                if vehicle.status == VehicleStatus.OFF_DUTY or not (
                    vehicle.available_from <= timestamp <= vehicle.available_until
                ):
                    continue
                if reserved[vehicle.vehicle_id] + order.demand_units > vehicle.capacity_units:
                    continue
                result = solver(self.graph, cursor.node_id, order.destination.node_id)
                if result is not None:
                    candidates.append((result.cost, vehicle.vehicle_id, vehicle, result))
            if not candidates:
                continue
            cost, _, vehicle, result = min(candidates, key=lambda item: (item[0], item[1]))
            reserved[vehicle.vehicle_id] += order.demand_units
            cursors[vehicle.vehicle_id] = order.destination
            vehicle.load_units = reserved[vehicle.vehicle_id]
            vehicle.status = VehicleStatus.BUSY
            order.status = order.status.IN_TRANSIT
            order.assigned_vehicle_id = vehicle.vehicle_id
            routes.append(DispatchRoute(vehicle.vehicle_id, order.order_id, result.path, cost, self.algorithm))
        return routes

    @staticmethod
    def distance_fallback(order: Order, vehicle: Vehicle) -> float:
        return FleetEngine.distance_km(vehicle.current_location, order.destination)
