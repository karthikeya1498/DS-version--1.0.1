"""A* shortest path with coordinate-based Euclidean heuristic."""
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.dijkstra import PathResult, _reconstruct
from src.dsa.heaps.priority_queue import PriorityQueue

def _heuristic(graph, current, goal, scale=1.0):
    a, b = graph.nodes[current], graph.nodes[goal]
    return scale * (((a.latitude - b.latitude) ** 2 + (a.longitude - b.longitude) ** 2) ** 0.5)

def shortest_path(graph: RoadGraph, start: str, goal: str, heuristic_scale=1.0) -> PathResult | None:
    if start not in graph.nodes or goal not in graph.nodes: raise KeyError('start and goal must exist')
    queue, distances, previous, visited = PriorityQueue(), {start: 0.0}, {}, 0
    if heuristic_scale < 0: raise ValueError('heuristic_scale must be non-negative')
    queue.push(_heuristic(graph, start, goal, heuristic_scale), start)
    while queue:
        _, current = queue.pop()
        visited += 1
        if current == goal: break
        for edge in graph.neighbors(current):
            candidate = distances[current] + edge.weight
            if candidate < distances.get(edge.target, float('inf')):
                distances[edge.target] = candidate; previous[edge.target] = current
                queue.push(candidate + _heuristic(graph, edge.target, goal, heuristic_scale), edge.target)
    if goal not in distances: return None
    return PathResult(_reconstruct(previous, start, goal), distances[goal], visited)
