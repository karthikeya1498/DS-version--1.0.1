from datetime import UTC, datetime, timedelta

from src.common.contracts import RoutePlan
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.phase3_engine import (
    ConstraintEngine,
    Objective,
    ObjectiveWeights,
    Phase3Solver,
    Prediction,
    SimulatedAnnealingSolver,
    minimum_feasible,
    select_capacity_subset,
)
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle


def graph() -> RoadGraph:
    result = RoadGraph()
    for node in range(4):
        result.add_node(Node(str(node), latitude=float(node), longitude=float(node)))
    result.add_edge(Edge("0", "1", 1.0), bidirectional=True)
    result.add_edge(Edge("1", "2", 1.0), bidirectional=True)
    result.add_edge(Edge("2", "3", 1.0), bidirectional=True)
    return result


def order(order_id="o1", node="2", demand=2):
    now = datetime(2026, 1, 1, 8, tzinfo=UTC)
    loc = Location(node, "z1", float(node), float(node))
    base = Location("0", "z0")
    return Order(
        order_id, base, loc, demand, now, TimeWindow(now, now + timedelta(hours=2)), priority=2
    )


def vehicle(capacity=5):
    now = datetime(2026, 1, 1, 8, tzinfo=UTC)
    return Vehicle("v1", Location("0", "z0"), capacity, now, now + timedelta(hours=8))


def test_objective_weights_and_capacity_dp():
    objective = Objective(
        ObjectiveWeights(distance=2, fuel=0, lateness=10, unserved=100, vehicle_usage=5)
    )
    assert (
        objective.score(distance_km=3, lateness_minutes=2, unserved_orders=1, activated_vehicles=1)
        == 131
    )
    assert select_capacity_subset([("a", 2, 5), ("b", 3, 8), ("c", 4, 9)], 5) == ("a", "b")


def test_binary_search_finds_minimum_feasible_fleet():
    assert minimum_feasible(1, 10, lambda count: count >= 4) == 4
    assert minimum_feasible(1, 3, lambda count: count >= 4) is None


def test_constraint_engine_rejects_capacity_and_unknown_order():
    report = ConstraintEngine().check_order_vehicle(order(demand=6), vehicle(capacity=5))
    assert not report.feasible and "capacity_exceeded:o1" in report.violations
    route_report = ConstraintEngine().check_route(
        RoutePlan("v1", ("missing",), ("0",), 0), [order()], [vehicle()]
    )
    assert not route_report.feasible and "unknown_order:missing" in route_report.violations


def test_phase3_greedy_connects_prediction_to_graph_route():
    solver = Phase3Solver(GraphDispatchRouter(graph()))
    result = solver.solve(
        [order()],
        [vehicle()],
        {"o1": Prediction(demand=2, eta_minutes=3, late_risk=0.1)},
        method="greedy",
    )
    assert result.served_orders == 1
    assert result.unserved_orders == 0
    assert result.routes[0].node_path == ("0", "1", "2")
    assert result.routes[0].vehicle_id == "v1"


def test_genetic_operator_preserves_route_permutation():
    solver = Phase3Solver(GraphDispatchRouter(graph()))
    route, value = solver.optimize_sequence(
        ["0", "3", "1", "2", "0"],
        lambda path: sum(abs(int(path[i + 1]) - int(path[i])) for i in range(len(path) - 1)),
        method="genetic",
    )
    assert route[0] == route[-1] == "0"
    assert sorted(route[1:-1]) == ["1", "2", "3"]
    assert value <= 8


def test_simulated_annealing_never_returns_worse_best_solution():
    optimizer = SimulatedAnnealingSolver(seed=42, iterations=100)
    initial = ["0", "1", "2", "3", "0"]
    result, cost = optimizer.optimize(
        initial,
        lambda route: sum(abs(int(route[i + 1]) - int(route[i])) for i in range(len(route) - 1)),
    )
    assert cost <= 6
    assert result[0] == "0" and result[-1] == "0"
