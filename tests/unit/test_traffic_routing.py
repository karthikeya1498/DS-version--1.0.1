from datetime import UTC, datetime

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.dsa.graphs.traffic import TrafficAwareGraph
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, TrafficState, Vehicle


def make_graph():
    graph = RoadGraph()
    for node_id, longitude in [("a", 0), ("b", 1), ("c", 2)]:
        graph.add_node(Node(node_id, 0, longitude))
    graph.add_edge(Edge("a", "b", 1), bidirectional=True)
    graph.add_edge(Edge("b", "c", 1), bidirectional=True)
    graph.add_edge(Edge("a", "c", 3), bidirectional=True)
    return graph


def test_traffic_updates_only_dynamic_weights_and_reset_restores_base():
    graph = make_graph()
    dynamic = TrafficAwareGraph(graph)
    traffic = TrafficState(datetime(2026, 1, 1, tzinfo=UTC), {"zone-c": 4.0})
    dynamic.apply_traffic(traffic)
    assert next(e.weight for e in graph.neighbors("b") if e.target == "c") == 4.0
    dynamic.reset()
    assert next(e.weight for e in graph.neighbors("b") if e.target == "c") == 1.0


def test_router_selects_lowest_travel_cost_vehicle():
    graph = make_graph()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    destination = Location("c", "zone-c", 0, 2)
    origin = Location("a", "zone-a", 0, 0)
    order = Order("o1", origin, destination, 1, now, TimeWindow(now, now.replace(hour=2)))
    vehicles = [
        Vehicle("far", Location("b", "zone-b", 0, 1), 5, now, now.replace(hour=2)),
        Vehicle("near", origin, 5, now, now.replace(hour=2)),
    ]
    route = GraphDispatchRouter(graph, "dijkstra").route(order, vehicles)
    assert route and route.vehicle_id == "far" and route.path == ("b", "c")
