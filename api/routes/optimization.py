from dataclasses import asdict
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.phase3_engine import Phase3Solver, Prediction
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
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
    result = Phase3Solver(GraphDispatchRouter(graph)).solve(
        [order],
        [vehicle],
        {"demo-order": Prediction(demand=1, eta_minutes=2, late_risk=0.01)},
        method="greedy",
    )
    return {
        "strategy": "graph_dispatch",
        "solver_strategy": result.strategy,
        "total_cost": result.total_cost,
        "served_orders": result.served_orders,
        "unserved_orders": result.unserved_orders,
        "runtime_ms": result.runtime_ms,
        "routes": [asdict(route) for route in result.routes],
    }
