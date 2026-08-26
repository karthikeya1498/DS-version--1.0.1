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
    def __init__(self, graph: RoadGraph, algorithm: str = 'astar') -> None:
        if algorithm not in {'astar', 'dijkstra'}: raise ValueError("algorithm must be 'astar' or 'dijkstra'")
        self.graph, self.algorithm = graph, algorithm

    def route(self, order: Order, vehicles: list[Vehicle], timestamp=None) -> DispatchRoute | None:
        timestamp = timestamp or order.created_at
        candidates = [v for v in vehicles if v.can_accept(order.demand_units, timestamp) and v.current_location.node_id in self.graph.nodes]
        routes = []
        solver = astar if self.algorithm == 'astar' else dijkstra
        for vehicle in candidates:
            result = solver(self.graph, vehicle.current_location.node_id, order.destination.node_id)
            if result is not None: routes.append((result.cost, vehicle.vehicle_id, vehicle, result))
        if not routes: return None
        cost, _, vehicle, result = min(routes, key=lambda item: (item[0], item[1]))
        vehicle.status = VehicleStatus.BUSY
        vehicle.load_units += order.demand_units
        order.status = order.status.IN_TRANSIT
        order.assigned_vehicle_id = vehicle.vehicle_id
        return DispatchRoute(vehicle.vehicle_id, order.order_id, result.path, cost, self.algorithm)

    @staticmethod
    def distance_fallback(order: Order, vehicle: Vehicle) -> float:
        return FleetEngine.distance_km(vehicle.current_location, order.destination)
