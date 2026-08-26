from datetime import datetime, timezone, timedelta
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.ml.demand.baseline import SeasonalMean
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle

def test_forecast_output_can_drive_routing_capacity():
    forecast = SeasonalMean().fit([3, 4, 5]).predict(1)[0]
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    graph = RoadGraph()
    for node_id, longitude in [('a', 0), ('b', 1)]: graph.add_node(Node(node_id, 0, longitude))
    graph.add_edge(Edge('a', 'b', 1), bidirectional=True)
    order = Order('forecast-order', Location('a', 'zone-a', 0, 0), Location('b', 'zone-b', 0, 1), max(1, round(forecast)), now, TimeWindow(now, now + timedelta(hours=2)))
    vehicle = Vehicle('forecast-vehicle', order.origin, 5, now, now + timedelta(hours=8))
    route = GraphDispatchRouter(graph, 'astar').route(order, [vehicle])
    assert route is not None
    assert route.path == ('a', 'b')
    assert vehicle.load_units == order.demand_units
