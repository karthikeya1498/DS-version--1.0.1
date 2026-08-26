"""Adjacency-list weighted graph for road networks."""

from __future__ import annotations

from collections import deque

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.node import Node


class RoadGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.adjacency: dict[str, list[Edge]] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node
        self.adjacency.setdefault(node.node_id, [])

    def add_edge(self, edge: Edge, bidirectional: bool = False) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise KeyError("both edge endpoints must exist as nodes")
        self.adjacency[edge.source].append(edge)
        if bidirectional:
            self.adjacency[edge.target].append(Edge(edge.target, edge.source, edge.weight))

    def neighbors(self, node_id: str) -> tuple[Edge, ...]:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        return tuple(self.adjacency[node_id])

    def bfs(self, start: str) -> list[str]:
        if start not in self.nodes:
            raise KeyError(start)
        seen, order, queue = {start}, [], deque([start])
        while queue:
            current = queue.popleft()
            order.append(current)
            for edge in self.adjacency[current]:
                if edge.target not in seen:
                    seen.add(edge.target)
                    queue.append(edge.target)
        return order
