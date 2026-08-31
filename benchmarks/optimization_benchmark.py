"""Benchmark suite evaluating optimization metaheuristics and exact solvers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any

import pandas as pd

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.objectives.cost import ObjectiveConfig
from src.optimization.phase3_engine import Objective, Phase3Solver
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle


def generate_benchmark_instance(order_count: int, vehicle_count: int) -> tuple[RoadGraph, list[Order], list[Vehicle]]:
    graph = RoadGraph()
    now = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)

    # Grid of nodes
    side = max(4, int(order_count**0.5) + 2)
    for r in range(side):
        for c in range(side):
            n_id = f"node_{r}_{c}"
            graph.add_node(Node(n_id, 12.9 + r * 0.01, 77.5 + c * 0.01))

    # Grid edges
    for r in range(side):
        for c in range(side):
            u = f"node_{r}_{c}"
            if r + 1 < side:
                graph.add_edge(Edge(u, f"node_{r+1}_{c}", 1.5), bidirectional=True)
            if c + 1 < side:
                graph.add_edge(Edge(u, f"node_{r}_{c+1}", 1.5), bidirectional=True)

    depot = Location("node_0_0", "zone_0", 12.9, 77.5)
    all_node_ids = list(graph.nodes.keys())

    orders = []
    for i in range(order_count):
        dest_node = all_node_ids[(i + 1) % len(all_node_ids)]
        loc = Location(dest_node, f"zone_{i % 4}", graph.nodes[dest_node].latitude, graph.nodes[dest_node].longitude)
        orders.append(
            Order(
                order_id=f"ord_{i:03d}",
                origin=depot,
                destination=loc,
                demand_units=2,
                created_at=now,
                time_window=TimeWindow(now, now + timedelta(hours=4)),
                priority=1 + (i % 3),
            )
        )

    vehicles = [
        Vehicle(
            vehicle_id=f"veh_{j:02d}",
            home_base=depot,
            capacity_units=max(20, (order_count * 2) // vehicle_count + 10),
            available_from=now,
            available_until=now + timedelta(hours=8),
            current_location=depot,
        )
        for j in range(vehicle_count)
    ]

    return graph, orders, vehicles


def run_solver_benchmark(
    scales: tuple[int, ...] = (10, 25, 50),
    methods: tuple[str, ...] = ("greedy", "greedy_2opt", "simulated_annealing", "tabu_search", "genetic", "ortools"),
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for n_orders in scales:
        n_vehicles = max(2, n_orders // 5)
        graph, orders, vehicles = generate_benchmark_instance(n_orders, n_vehicles)
        router = GraphDispatchRouter(graph)
        solver = Phase3Solver(router, objective=Objective(ObjectiveConfig()))

        for method in methods:
            start_t = perf_counter()
            result = solver.solve(orders, vehicles, method=method)
            wall_ms = (perf_counter() - start_t) * 1000

            rows.append({
                "scale_orders": n_orders,
                "fleet_size": n_vehicles,
                "algorithm": method,
                "total_cost": round(result.total_cost, 2),
                "served_orders": result.served_orders,
                "unserved_orders": result.unserved_orders,
                "distance_km": round(result.diagnostics.get("distance_km", 0.0), 2),
                "runtime_ms": round(wall_ms, 2),
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=" * 60)
    print("  OPTIMA-X: MULTI-SOLVER OPTIMIZATION BENCHMARK  ")
    print("=" * 60)
    df = run_solver_benchmark(scales=(10, 25, 50))
    print(df.to_string(index=False))
