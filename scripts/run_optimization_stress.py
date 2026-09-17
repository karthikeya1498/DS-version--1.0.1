"""Stress-test Phase 3 with a 50-order batch and 50-unit capacity.

Author: Karthikeya
The same deterministic road graph, order batch, fleet, objective, and seed
are reused across the available route-order strategies.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.phase3_engine import Objective, Phase3Solver, Prediction
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle

METHODS = ("greedy", "greedy_2opt", "greedy_3opt", "simulated_annealing", "genetic")


def build_graph(nodes: int) -> RoadGraph:
    graph = RoadGraph()
    for index in range(nodes):
        graph.add_node(Node(str(index), latitude=float(index), longitude=float(index)))
    for index in range(nodes - 1):
        graph.add_edge(Edge(str(index), str(index + 1), 1.0 + (index % 7) * 0.05), bidirectional=True)
    return graph


def make_orders(batch_size: int, nodes: int) -> list[Order]:
    start = datetime(2026, 1, 1, 8, tzinfo=UTC)
    base = Location("0", "base")
    return [Order(f"stress-{index:03d}", base, Location(str((index % (nodes - 1)) + 1), "stress-zone", 0.0, float(index % (nodes - 1) + 1),), (index % 4) + 1, start, TimeWindow(start, start + timedelta(hours=12)), priority=(index % 5) + 1) for index in range(batch_size)]


def run(batch_size: int, fleet_capacity: int, vehicles_count: int, output: str | Path) -> dict[str, object]:
    nodes = max(51, batch_size + 1)
    graph = build_graph(nodes)
    template_orders = make_orders(batch_size, nodes)
    predictions = {order.order_id: Prediction(float(order.demand_units), eta_minutes=float(order.destination.longitude), late_risk=0.01 * order.priority, uncertainty=0.01) for order in template_orders}
    results = []
    shift_start = datetime(2026, 1, 1, 8, tzinfo=UTC)
    shift_end = shift_start + timedelta(hours=12)
    for method in METHODS:
        orders = make_orders(batch_size, nodes)
        vehicles = [Vehicle(f"stress-v{index:02d}", Location(str(index % 5), f"base-{index % 5}"), fleet_capacity, shift_start, shift_end) for index in range(vehicles_count)]
        solver = Phase3Solver(GraphDispatchRouter(graph), Objective())
        started = perf_counter()
        result = solver.solve(orders, vehicles, predictions, method=method)
        elapsed_ms = (perf_counter() - started) * 1000
        results.append({"method": method, "runtime_ms": elapsed_ms, "decision_cost": result.total_cost, "distance_km": sum(route.distance_km for route in result.routes), "lateness_minutes": sum(route.lateness_minutes for route in result.routes), "served_orders": result.served_orders, "unserved_orders": result.unserved_orders, "feasible": all(route.feasible for route in result.routes), "routes": len(result.routes)})
    payload = {"scenario": {"orders": batch_size, "fleet_capacity_units_per_vehicle": fleet_capacity, "vehicles": vehicles_count, "graph_nodes": nodes, "seed": 42}, "methods": results}
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", type=int, default=50)
    parser.add_argument("--fleet-capacity", type=int, default=50)
    parser.add_argument("--vehicles", type=int, default=10)
    parser.add_argument("--output", default="data/processed/phase3_optimization_stress.json")
    args = parser.parse_args()
    if min(args.orders, args.fleet_capacity, args.vehicles) < 1:
        raise SystemExit("orders, fleet-capacity, and vehicles must be positive")
    print(json.dumps(run(args.orders, args.fleet_capacity, args.vehicles, args.output), indent=2))


if __name__ == "__main__":
    main()
