"""Graph topological and network traffic feature engineering."""
from __future__ import annotations

from typing import Any

from src.dsa.graphs.graph import RoadGraph


def extract_node_graph_features(graph: RoadGraph, node_id: str) -> dict[str, float]:
    """Extract degree and local network density features for a road node."""
    if node_id not in graph.nodes:
        return {"out_degree": 0.0, "in_degree": 0.0, "total_degree": 0.0, "avg_outgoing_weight": 0.0}

    out_edges = graph.neighbors(node_id)
    out_degree = len(out_edges)
    avg_weight = (sum(e.weight for e in out_edges) / max(1, out_degree)) if out_degree else 0.0

    in_degree = sum(1 for u in graph.adjacency for e in graph.adjacency[u] if e.target == node_id)

    return {
        "out_degree": float(out_degree),
        "in_degree": float(in_degree),
        "total_degree": float(out_degree + in_degree),
        "avg_outgoing_weight": float(avg_weight),
    }


def extract_path_graph_features(graph: RoadGraph, path_nodes: list[str]) -> dict[str, float]:
    """Extract path structural metrics (hops, total weight, max segment weight)."""
    if len(path_nodes) < 2:
        return {"hop_count": 0.0, "total_path_weight": 0.0, "max_segment_weight": 0.0, "avg_segment_weight": 0.0}

    weights = []
    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        edge = next((e for e in graph.neighbors(u) if e.target == v), None)
        if edge is not None:
            weights.append(edge.weight)
        else:
            weights.append(0.0)

    total_w = sum(weights)
    max_w = max(weights) if weights else 0.0
    avg_w = total_w / len(weights) if weights else 0.0

    return {
        "hop_count": float(len(path_nodes) - 1),
        "total_path_weight": float(total_w),
        "max_segment_weight": float(max_w),
        "avg_segment_weight": float(avg_w),
    }
