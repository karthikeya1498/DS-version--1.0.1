"""Scalability and high-throughput load benchmark for OPTIMA-X."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Any

import pandas as pd

from benchmarks.optimization_benchmark import generate_benchmark_instance
from src.optimization.objectives.cost import ObjectiveConfig
from src.optimization.phase3_engine import Objective, Phase3Solver
from src.optimization.routing.graph_dispatch import GraphDispatchRouter


def run_scalability_benchmark(order_batches: tuple[int, ...] = (50, 100, 200, 500)) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for n_orders in order_batches:
        n_vehicles = max(5, n_orders // 10)
        graph, orders, vehicles = generate_benchmark_instance(n_orders, n_vehicles)
        router = GraphDispatchRouter(graph)
        solver = Phase3Solver(router, objective=Objective(ObjectiveConfig()))

        start_t = perf_counter()
        result = solver.solve(orders, vehicles, method="greedy_2opt")
        wall_sec = perf_counter() - start_t

        throughput_ops = n_orders / max(wall_sec, 1e-4)

        rows.append({
            "order_volume": n_orders,
            "fleet_size": n_vehicles,
            "served_orders": result.served_orders,
            "unserved_orders": result.unserved_orders,
            "solve_time_sec": round(wall_sec, 3),
            "throughput_orders_per_sec": round(throughput_ops, 1),
            "total_cost": round(result.total_cost, 2),
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=" * 60)
    print("  OPTIMA-X: SCALABILITY & THROUGHPUT BENCHMARK  ")
    print("=" * 60)
    df = run_scalability_benchmark()
    print(df.to_string(index=False))
