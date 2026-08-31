"""
DSA Integration bridges connecting core data structures to the OPTIMA-X logistics engine.

Integrates:
- Segment Tree: Dynamic range queries for traffic congestion and speeds over time intervals.
- Fenwick Tree (BIT): Rolling cumulative demand aggregation and fast interval sum queries.
- Union-Find: Graph connectivity and island/reachability partition validation.
- Priority Queue: Real-time event scheduling and frontier exploration.
- 0/1 Knapsack DP: Optimal payload parcel selection under vehicle capacity limits.
"""
from __future__ import annotations

from typing import Iterable, Sequence

from src.dsa.dynamic_programming.knapsack import knapsack
from src.dsa.graphs.graph import RoadGraph
from src.dsa.trees.fenwick_tree import FenwickTree
from src.dsa.trees.segment_tree import SegmentTree
from src.dsa.union_find.disjoint_set import DisjointSet


class TrafficSpeedRangeQuery:
    """
    Dynamic range query engine for road speed/congestion profiles using SegmentTree.
    Allows O(log N) min, max, and aggregate queries over time windows.
    """

    def __init__(self, speeds: Sequence[float], aggregation: str = "min") -> None:
        if not speeds:
            raise ValueError("speeds sequence cannot be empty")
        self.raw_speeds = list(speeds)
        self.aggregation = aggregation
        combine_fn = min if aggregation == "min" else (max if aggregation == "max" else lambda a, b: a + b)
        self.tree = SegmentTree(self.raw_speeds, combine=combine_fn)

    def update_speed(self, time_index: int, new_speed: float) -> None:
        """Update traffic speed at a specific time step in O(log N)."""
        self.raw_speeds[time_index] = new_speed
        self.tree.update(time_index, new_speed)

    def query_interval(self, start_idx: int, end_idx: int) -> float:
        """Query worst-case (min), best-case (max), or sum speed in time window [start, end]."""
        return self.tree.query(start_idx, end_idx)


class CumulativeDemandMonitor:
    """
    Rolling demand and order volume tracker using Fenwick Tree (Binary Indexed Tree).
    Supports O(log N) point demand updates and O(log N) range demand queries.
    """

    def __init__(self, size: int) -> None:
        if size <= 0:
            raise ValueError("size must be positive")
        self.size = size
        self.bit = FenwickTree(size)

    def record_order_demand(self, time_index: int, demand_units: float) -> None:
        """Record newly arrived orders at time_index in O(log N)."""
        self.bit.update(time_index, demand_units)

    def cumulative_demand(self, time_index: int) -> float:
        """Total cumulative demand from step 0 to time_index."""
        return self.bit.prefix_sum(time_index)

    def range_demand(self, start_time: int, end_time: int) -> float:
        """Total demand within interval [start_time, end_time]."""
        return self.bit.range_sum(start_time, end_time)


class NetworkConnectivityEngine:
    """
    Road network partition and reachability validator using Disjoint Set (Union-Find).
    Verifies that all origin-destination pairs belong to the same connected component.
    """

    def __init__(self, graph: RoadGraph) -> None:
        self.graph = graph
        self.ds = DisjointSet()
        for node_id in graph.nodes:
            self.ds.find(node_id)
        for u in graph.adjacency:
            for edge in graph.adjacency[u]:
                self.ds.union(u, edge.target)

    def are_connected(self, node_a: str, node_b: str) -> bool:
        """Check if node_a can reach node_b within the connected road subnetwork."""
        if node_a not in self.graph.nodes or node_b not in self.graph.nodes:
            return False
        return self.ds.connected(node_a, node_b)

    def connected_component_count(self) -> int:
        """Count total isolated subgraphs in the road network."""
        roots = {self.ds.find(n) for n in self.graph.nodes}
        return len(roots)


class CapacityKnapsackSelector:
    """
    Solves optimal parcel selection for a single vehicle using 0/1 Knapsack DP.
    Selects the subset of pending orders that maximizes priority/revenue value
    while strictly respecting vehicle load capacity.
    """

    @staticmethod
    def select_orders(
        order_items: Sequence[tuple[str, int, float]],
        capacity: int,
    ) -> tuple[tuple[str, ...], float]:
        """
        order_items: list of (order_id, weight_demand, value_priority)
        capacity: vehicle remaining capacity units
        Returns: (tuple of selected order IDs, total value achieved)
        """
        if capacity <= 0 or not order_items:
            return (), 0.0
        weights = [item[1] for item in order_items]
        values = [item[2] for item in order_items]
        max_val, indices = knapsack(weights, values, capacity)
        selected_ids = tuple(order_items[i][0] for i in indices)
        return selected_ids, max_val
