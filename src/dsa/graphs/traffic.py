"""Dynamic traffic-aware edge weight management."""
from __future__ import annotations
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.simulation.models import TrafficState

class TrafficAwareGraph:
    def __init__(self, graph: RoadGraph) -> None:
        self.graph = graph
        self._base_weights: dict[tuple[str, str, int], float] = {}
        self._capture_base_weights()

    def _capture_base_weights(self) -> None:
        self._base_weights.clear()
        for source, edges in self.graph.adjacency.items():
            for index, edge in enumerate(edges):
                self._base_weights[(source, edge.target, index)] = edge.weight

    def apply_traffic(self, traffic: TrafficState) -> None:
        for source, edges in self.graph.adjacency.items():
            updated: list[Edge] = []
            for index, edge in enumerate(edges):
                base = self._base_weights[(source, edge.target, index)]
                target = self.graph.nodes[edge.target]
                multiplier = traffic.multiplier_for(getattr(target, "zone_id", f"zone-{target.node_id}"))
                if multiplier == 1.0:
                    multiplier = traffic.multiplier_for(target.node_id)
                updated.append(Edge(edge.source, edge.target, base * multiplier))
            self.graph.adjacency[source] = updated

    def reset(self) -> None:
        for source, edges in self.graph.adjacency.items():
            self.graph.adjacency[source] = [Edge(e.source, e.target, self._base_weights[(source, e.target, i)]) for i, e in enumerate(edges)]
