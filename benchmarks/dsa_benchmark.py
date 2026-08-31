"""Benchmark suite evaluating Core Data Structures & Algorithms performance."""

from __future__ import annotations

import random
from time import perf_counter
from typing import Any

import pandas as pd

from src.dsa.dsa_integration import CumulativeDemandMonitor, TrafficSpeedRangeQuery
from src.dsa.graphs.astar import shortest_path as astar_path
from src.dsa.graphs.dijkstra import shortest_path as dijkstra_path
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


def benchmark_segment_tree_vs_linear(
    n_elements: int = 10000, n_queries: int = 1000
) -> dict[str, float]:
    data = [random.uniform(10.0, 60.0) for _ in range(n_elements)]
    st = TrafficSpeedRangeQuery(data, aggregation="min")

    query_ranges = [
        sorted([random.randint(0, n_elements - 1), random.randint(0, n_elements - 1)])
        for _ in range(n_queries)
    ]

    # Segment Tree O(log N)
    start_t = perf_counter()
    for l, r in query_ranges:
        _ = st.query_interval(l, r)
    st_time = (perf_counter() - start_t) * 1000

    # Linear Scan O(N)
    start_t = perf_counter()
    for l, r in query_ranges:
        _ = min(data[l : r + 1])
    linear_time = (perf_counter() - start_t) * 1000

    return {
        "operation": "Range Min Query",
        "elements": n_elements,
        "queries": n_queries,
        "segment_tree_ms": round(st_time, 2),
        "linear_scan_ms": round(linear_time, 2),
        "speedup": round(linear_time / max(st_time, 1e-4), 2),
    }


def benchmark_fenwick_vs_linear(n_elements: int = 10000, n_updates: int = 1000) -> dict[str, float]:
    bit = CumulativeDemandMonitor(n_elements)
    linear_arr = [0.0] * n_elements

    updates = [
        (random.randint(0, n_elements - 1), random.uniform(1.0, 10.0)) for _ in range(n_updates)
    ]

    # Fenwick Tree O(log N)
    start_t = perf_counter()
    for idx, val in updates:
        bit.record_order_demand(idx, val)
        _ = bit.cumulative_demand(idx)
    fenwick_time = (perf_counter() - start_t) * 1000

    # Linear Array O(N) prefix sum
    start_t = perf_counter()
    for idx, val in updates:
        linear_arr[idx] += val
        _ = sum(linear_arr[: idx + 1])
    linear_time = (perf_counter() - start_t) * 1000

    return {
        "operation": "Point Update & Prefix Sum",
        "elements": n_elements,
        "operations": n_updates,
        "fenwick_tree_ms": round(fenwick_time, 2),
        "linear_array_ms": round(linear_time, 2),
        "speedup": round(linear_time / max(fenwick_time, 1e-4), 2),
    }


def benchmark_astar_vs_dijkstra(grid_size: int = 20) -> dict[str, Any]:
    graph = RoadGraph()
    for r in range(grid_size):
        for c in range(grid_size):
            graph.add_node(Node(f"n_{r}_{c}", 12.0 + r * 0.01, 77.0 + c * 0.01))

    for r in range(grid_size):
        for c in range(grid_size):
            u = f"n_{r}_{c}"
            if r + 1 < grid_size:
                graph.add_edge(Edge(u, f"n_{r + 1}_{c}", 1.0), bidirectional=True)
            if c + 1 < grid_size:
                graph.add_edge(Edge(u, f"n_{r}_{c + 1}", 1.0), bidirectional=True)

    src = "n_0_0"
    dst = f"n_{grid_size - 1}_{grid_size - 1}"

    start_t = perf_counter()
    dijk_res = dijkstra_path(graph, src, dst)
    dijk_time = (perf_counter() - start_t) * 1000

    start_t = perf_counter()
    astar_res = astar_path(graph, src, dst)
    astar_time = (perf_counter() - start_t) * 1000

    return {
        "grid_size": f"{grid_size}x{grid_size}",
        "nodes": len(graph.nodes),
        "dijkstra_ms": round(dijk_time, 2),
        "astar_ms": round(astar_time, 2),
        "cost_match": abs(dijk_res.cost - astar_res.cost) < 1e-5,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("  OPTIMA-X: DSA PERFORMANCE BENCHMARK  ")
    print("=" * 60)
    print(
        pd.DataFrame(
            [
                benchmark_segment_tree_vs_linear(),
                benchmark_fenwick_vs_linear(),
            ]
        ).to_string(index=False)
    )
    print("\nA* vs Dijkstra on 20x20 Grid:")
    print(pd.DataFrame([benchmark_astar_vs_dijkstra(20)]).to_string(index=False))
