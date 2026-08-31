"""Tests for admissible A* heuristic, consistency, and Dijkstra optimality equivalence."""

import pytest

from src.dsa.graphs.astar import create_admissible_heuristic, haversine_distance_km
from src.dsa.graphs.astar import shortest_path as astar_shortest_path
from src.dsa.graphs.dijkstra import shortest_path as dijkstra_shortest_path
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


@pytest.fixture
def geometric_grid_graph():
    """A 4x4 grid road graph with known coordinates."""
    g = RoadGraph()
    for r in range(4):
        for c in range(4):
            node_id = f"n_{r}_{c}"
            # Latitude and Longitude (spaced roughly 1 km apart)
            lat = 12.9716 + (r * 0.009)
            lon = 77.5946 + (c * 0.009)
            g.add_node(Node(node_id, lat, lon))

    # Add edges with Euclidean / Haversine distance as weights
    for r in range(4):
        for c in range(4):
            u_id = f"n_{r}_{c}"
            u_node = g.nodes[u_id]
            if r + 1 < 4:
                v_id = f"n_{r + 1}_{c}"
                v_node = g.nodes[v_id]
                weight = haversine_distance_km(u_node, v_node)
                g.add_edge(Edge(u_id, v_id, weight), bidirectional=True)
            if c + 1 < 4:
                v_id = f"n_{r}_{c + 1}"
                v_node = g.nodes[v_id]
                weight = haversine_distance_km(u_node, v_node)
                g.add_edge(Edge(u_id, v_id, weight), bidirectional=True)
    return g


def test_haversine_formula():
    n1 = Node("blr", 12.9716, 77.5946)
    n2 = Node("del", 28.7041, 77.1025)
    dist = haversine_distance_km(n1, n2)
    # Bangalore to Delhi is approx 1740 km
    assert 1700 < dist < 1800


def test_astar_dijkstra_optimality_equivalence(geometric_grid_graph):
    """Admissible A* must produce the exact same path cost as Dijkstra."""
    start = "n_0_0"
    goal = "n_3_3"

    dijkstra_res = dijkstra_shortest_path(geometric_grid_graph, start, goal)
    h_fn = create_admissible_heuristic(geometric_grid_graph, metric="haversine")
    astar_res = astar_shortest_path(geometric_grid_graph, start, goal, heuristic_fn=h_fn)

    assert dijkstra_res is not None
    assert astar_res is not None
    # Path costs must be identical within floating point tolerance
    assert abs(dijkstra_res.cost - astar_res.cost) < 1e-6
    # A* should visit fewer or equal nodes than Dijkstra
    assert astar_res.visited <= dijkstra_res.visited


def test_heuristic_admissibility_and_consistency(geometric_grid_graph):
    """
    Test Admissibility: h(u, goal) <= true_cost(u, goal)
    Test Consistency: h(u, goal) <= cost(u, v) + h(v, goal)
    """
    goal = "n_3_3"
    h_fn = create_admissible_heuristic(geometric_grid_graph, metric="haversine")

    for node_id in geometric_grid_graph.nodes:
        dijkstra_res = dijkstra_shortest_path(geometric_grid_graph, node_id, goal)
        if dijkstra_res is not None:
            h_val = h_fn(node_id, goal)
            # Admissibility check: heuristic lower bound never overestimates
            assert h_val <= dijkstra_res.cost + 1e-9

        # Consistency (triangle inequality) check
        for edge in geometric_grid_graph.neighbors(node_id):
            h_u = h_fn(node_id, goal)
            h_v = h_fn(edge.target, goal)
            assert h_u <= edge.weight + h_v + 1e-9
