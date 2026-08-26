from datetime import UTC, datetime, timedelta

from fastapi import APIRouter

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.optimization.solver.hybrid_solver import HybridSolver
from src.simulation.models import Location, Order, TimeWindow, Vehicle

router = APIRouter(prefix="/optimization", tags=["optimization"])


@router.get("/demo")
def optimization_demo():
    now = datetime.now(UTC)
    graph = RoadGraph()
    for n in ["a", "b", "c"]:
        graph.add_node(Node(n, 0, ord(n) - 97))
    graph.add_edge(Edge("a", "b", 1), bidirectional=True)
    graph.add_edge(Edge("b", "c", 1), bidirectional=True)
    origin, destination = Location("a", "zone-a", 0, 0), Location("c", "zone-c", 0, 2)
    order = Order(
        "demo-order", origin, destination, 1, now, TimeWindow(now, now + timedelta(hours=2))
    )
    vehicle = Vehicle("demo-vehicle", origin, 10, now, now + timedelta(hours=8))
    return HybridSolver(GraphDispatchRouter(graph)).solve([order], [vehicle])
