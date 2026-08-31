"""Benchmark A* heuristic scales on deterministic irregular obstacle grids."""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dsa.graphs.astar import shortest_path as astar
from src.dsa.graphs.dijkstra import shortest_path as dijkstra
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


def build_obstacle_grid(side=50, obstacle_rate=0.18, seed=42):
    rng = random.Random(seed)
    blocked = {(r, c) for r in range(side) for c in range(side) if rng.random() < obstacle_rate}
    start, goal = (0, 0), (side - 1, side - 1)
    blocked -= {start, goal}
    graph = RoadGraph()
    for r in range(side):
        for c in range(side):
            if (r, c) not in blocked:
                graph.add_node(Node(f"{r},{c}", r / (side - 1), c / (side - 1)))
    for node_id in list(graph.nodes):
        row, col = map(int, node_id.split(","))
        for dr, dc in ((1, 0), (0, 1)):
            nr, nc = row + dr, col + dc
            if f"{nr},{nc}" in graph.nodes:
                graph.add_edge(
                    Edge(node_id, f"{nr},{nc}", 1.0 + rng.random() * 0.25), bidirectional=True
                )
    return graph, blocked


def run(
    sides=(25, 50, 75),
    scales=("raw", "calibrated"),
    repetitions=3,
    output="data/processed/obstacle_benchmark.csv",
):
    rows = []
    for side in sides:
        graph, blocked = build_obstacle_grid(side)
        dijkstra_result = dijkstra(graph, "0,0", f"{side - 1},{side - 1}")
        if dijkstra_result is None:
            continue
        for label in scales:
            scale = 1.0 if label == "raw" else side - 1
            samples = []
            for _ in range(repetitions):
                began = perf_counter()
                result = astar(graph, "0,0", f"{side - 1},{side - 1}", heuristic_scale=scale)
                elapsed = (perf_counter() - began) * 1000
                samples.append((elapsed, result.visited, result.cost))
            rows.append(
                {
                    "grid_side": side,
                    "nodes": len(graph.nodes),
                    "blocked_nodes": len(blocked),
                    "obstacle_rate": len(blocked) / (side * side),
                    "heuristic": label,
                    "heuristic_scale": scale,
                    "runtime_ms_mean": sum(x[0] for x in samples) / len(samples),
                    "visited_nodes_mean": sum(x[1] for x in samples) / len(samples),
                    "path_cost": samples[0][2],
                    "same_cost_as_dijkstra": abs(samples[0][2] - dijkstra_result.cost) < 1e-9,
                }
            )
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == "__main__":
    for row in run():
        print(row)
