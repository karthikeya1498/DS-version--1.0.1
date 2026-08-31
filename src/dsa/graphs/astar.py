"""A* shortest path with mathematically admissible and consistent heuristics."""
from __future__ import annotations

import math
from typing import Callable

from src.dsa.graphs.dijkstra import PathResult, _reconstruct
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.dsa.heaps.priority_queue import PriorityQueue

EARTH_RADIUS_KM = 6371.0088


def haversine_distance_km(a: Node, b: Node) -> float:
    """Great-circle distance between two geographic coordinates in kilometers."""
    lat1, lon1 = math.radians(a.latitude), math.radians(a.longitude)
    lat2, lon2 = math.radians(b.latitude), math.radians(b.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    val = (math.sin(dlat / 2.0) ** 2) + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2.0) ** 2)
    val = min(1.0, max(0.0, val))
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(val))


def euclidean_distance(a: Node, b: Node) -> float:
    """Euclidean distance in cartesian plane."""
    return math.sqrt((a.latitude - b.latitude) ** 2 + (a.longitude - b.longitude) ** 2)


def create_admissible_heuristic(
    graph: RoadGraph,
    metric: str = "haversine",
    max_speed_kmh: float | None = None,
    distance_scale: float = 1.0,
) -> Callable[[str, str], float]:
    """
    Construct an admissible heuristic function h(u, v).
    If edge weights are travel time in minutes/hours and max_speed_kmh is provided:
        h(u, v) = distance(u, v) / max_speed
    This guarantees h(u, v) <= true_remaining_cost (admissibility)
    and h(u, v) <= cost(u, w) + h(w, v) (consistency / triangle inequality).
    """
    def heuristic(current: str, goal: str) -> float:
        if current == goal:
            return 0.0
        node_a = graph.nodes.get(current)
        node_b = graph.nodes.get(goal)
        if node_a is None or node_b is None:
            return 0.0
        if metric == "haversine":
            dist = haversine_distance_km(node_a, node_b)
        else:
            dist = euclidean_distance(node_a, node_b)
        if max_speed_kmh is not None and max_speed_kmh > 0:
            # Travel time in hours or scaled units
            return (dist / max_speed_kmh) * distance_scale
        return dist * distance_scale

    return heuristic


def shortest_path(
    graph: RoadGraph,
    start: str,
    goal: str,
    heuristic_scale: float = 1.0,
    heuristic_fn: Callable[[str, str], float] | None = None,
) -> PathResult | None:
    """
    Compute optimal shortest path using A* search.
    Guaranteed optimal and Dijkstra-equivalent when heuristic is admissible.
    """
    if start not in graph.nodes or goal not in graph.nodes:
        raise KeyError("start and goal must exist")
    if heuristic_scale < 0:
        raise ValueError("heuristic_scale must be non-negative")

    if heuristic_fn is None:
        raw_h = create_admissible_heuristic(graph, metric="euclidean")
    else:
        raw_h = heuristic_fn

    def h(u: str) -> float:
        return heuristic_scale * raw_h(u, goal)

    queue = PriorityQueue()
    g_scores: dict[str, float] = {start: 0.0}
    previous: dict[str, str] = {}
    visited = 0

    queue.push(h(start), start)

    while queue:
        f_cost, current = queue.pop()
        visited += 1

        if current == goal:
            break

        current_g = g_scores[current]

        for edge in graph.neighbors(current):
            tentative_g = current_g + edge.weight
            if tentative_g < g_scores.get(edge.target, float("inf")):
                g_scores[edge.target] = tentative_g
                previous[edge.target] = current
                f_score = tentative_g + h(edge.target)
                queue.push(f_score, edge.target)

    if goal not in g_scores:
        return None

    return PathResult(_reconstruct(previous, start, goal), g_scores[goal], visited)
