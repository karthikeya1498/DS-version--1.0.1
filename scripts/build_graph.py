"""Build the in-memory road graph from nodes and edges CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


def build(nodes_csv: str | Path, edges_csv: str | Path) -> RoadGraph:
    graph = RoadGraph()
    with Path(nodes_csv).open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            graph.add_node(Node(row["node_id"], float(row["latitude"]), float(row["longitude"])))
    with Path(edges_csv).open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            graph.add_edge(
                Edge(
                    row["source"],
                    row["target"],
                    float(row.get("cost", row.get("travel_time_min", 1))),
                ),
                bidirectional=row.get("bidirectional", "false").lower() == "true",
            )
    return graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", required=True)
    parser.add_argument("--edges", required=True)
    args = parser.parse_args()
    graph = build(args.nodes, args.edges)
    print(
        json.dumps(
            {
                "nodes": len(graph.nodes),
                "edges": sum(len(v) for v in graph.adjacency.values()),
                "graph_built": True,
            },
            indent=2,
        )
    )
