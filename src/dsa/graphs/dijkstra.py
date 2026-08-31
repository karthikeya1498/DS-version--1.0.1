"""Dijkstra shortest path for non-negative weighted graphs."""

from dataclasses import dataclass

from src.dsa.graphs.graph import RoadGraph
from src.dsa.heaps.priority_queue import PriorityQueue


@dataclass(frozen=True)
class PathResult:
    path: tuple[str, ...]
    cost: float
    visited: int


def shortest_path(graph: RoadGraph, start: str, goal: str) -> PathResult | None:
    if start not in graph.nodes or goal not in graph.nodes:
        raise KeyError("start and goal must exist")
    queue, distances, previous, visited = PriorityQueue(), {start: 0.0}, {}, 0
    queue.push(0.0, start)
    while queue:
        cost, current = queue.pop()
        if cost != distances.get(current):
            continue
        visited += 1
        if current == goal:
            break
        for edge in graph.neighbors(current):
            candidate = cost + edge.weight
            if candidate < distances.get(edge.target, float("inf")):
                distances[edge.target] = candidate
                previous[edge.target] = current
                queue.push(candidate, edge.target)
    if goal not in distances:
        return None
    return PathResult(_reconstruct(previous, start, goal), distances[goal], visited)


def _reconstruct(previous, start, goal):
    path, current = [goal], goal
    while current != start:
        current = previous[current]
        path.append(current)
    return tuple(reversed(path))
