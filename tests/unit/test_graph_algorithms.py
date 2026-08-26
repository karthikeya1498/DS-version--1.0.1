import pytest

from src.dsa.graphs.astar import shortest_path as astar
from src.dsa.graphs.dijkstra import shortest_path as dijkstra
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.dsa.heaps.priority_queue import PriorityQueue


def graph():
    g = RoadGraph()
    for i in range(5):
        g.add_node(Node(str(i), latitude=0, longitude=i))
    g.add_edge(Edge("0", "1", 2), bidirectional=True)
    g.add_edge(Edge("1", "2", 2), bidirectional=True)
    g.add_edge(Edge("0", "3", 1), bidirectional=True)
    g.add_edge(Edge("3", "2", 1), bidirectional=True)
    g.add_edge(Edge("2", "4", 3), bidirectional=True)
    return g


def test_dijkstra_finds_lowest_cost_path():
    result = dijkstra(graph(), "0", "4")
    assert result and result.path == ("0", "3", "2", "4") and result.cost == 5


def test_astar_matches_dijkstra_cost():
    assert astar(graph(), "0", "4").cost == dijkstra(graph(), "0", "4").cost


def test_priority_queue_is_stable_for_equal_priorities():
    q = PriorityQueue()
    q.push(1, "first")
    q.push(1, "second")
    assert q.pop() == (1, "first")
    assert q.pop() == (1, "second")


def test_negative_edges_are_rejected():
    with pytest.raises(ValueError):
        Edge("a", "b", -1)
