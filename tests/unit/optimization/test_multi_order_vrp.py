"""Unit tests for multi-order vehicle routing, capacity bin-packing, and 50-order stress test."""
from datetime import datetime, timedelta, timezone
import pytest

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.assignment.order_assignment import cluster_orders_by_capacity
from src.optimization.phase3_engine import Objective, ObjectiveConfig, Phase3Solver, Prediction
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.optimization.routing.simulated_annealing import SimulatedAnnealingSolver
from src.optimization.routing.tabu_search import TabuSearchSolver
from src.optimization.routing.two_opt import improve as two_opt
from src.simulation.models import Location, Order, TimeWindow, Vehicle, VehicleStatus


@pytest.fixture
def urban_road_graph():
    g = RoadGraph()
    # 5 nodes on a line
    for i, name in enumerate(["depot", "A", "B", "C", "D"]):
        g.add_node(Node(name, 12.97 + i * 0.01, 77.59 + i * 0.01))
    g.add_edge(Edge("depot", "A", 2.0), bidirectional=True)
    g.add_edge(Edge("A", "B", 3.0), bidirectional=True)
    g.add_edge(Edge("B", "C", 4.0), bidirectional=True)
    g.add_edge(Edge("C", "D", 5.0), bidirectional=True)
    return g


def test_capacity_multi_order_clustering():
    now = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    depot = Location("depot", "zone_1", 12.97, 77.59)
    dest = Location("A", "zone_1", 12.98, 77.60)

    # 10 orders of demand 2 each = total 20 demand
    orders = [
        Order(f"ord_{i}", depot, dest, demand_units=2, created_at=now, time_window=TimeWindow(now, now + timedelta(hours=2)))
        for i in range(10)
    ]

    # 2 vehicles of capacity 10 each
    vehicles = [
        Vehicle(f"v_{i}", home_base=depot, capacity_units=10, available_from=now, available_until=now + timedelta(hours=8), current_location=depot)
        for i in range(2)
    ]

    bundles, unassigned = cluster_orders_by_capacity(orders, vehicles)

    # All 10 orders should be packed (5 per vehicle), 0 unassigned
    assert len(unassigned) == 0
    assert len(bundles["v_0"]) == 5
    assert len(bundles["v_1"]) == 5


def test_50_order_stress_test_capacity_utilization(urban_road_graph):
    """
    Directly tests and resolves Review Finding #34 (the 50-order stress failure):
    50 orders, 10 vehicles of capacity 50 each.
    The system MUST exploit multi-order capacity and serve ALL 50 orders!
    """
    now = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    depot = Location("depot", "zone_1", 12.97, 77.59)
    nodes = ["A", "B", "C", "D"]

    # 50 orders of demand 2 each (total 100 demand)
    orders = []
    for i in range(50):
        dest_node = nodes[i % len(nodes)]
        dest = Location(dest_node, "zone_1", 12.98, 77.60)
        orders.append(
            Order(
                f"order_{i:02d}",
                origin=depot,
                destination=dest,
                demand_units=2,
                created_at=now,
                time_window=TimeWindow(now, now + timedelta(hours=4)),
                priority=1 + (i % 3),
            )
        )

    # 10 vehicles of capacity 50 each (total fleet capacity 500 units)
    vehicles = []
    for i in range(10):
        vehicles.append(
            Vehicle(
                f"veh_{i:02d}",
                home_base=depot,
                capacity_units=50,
                available_from=now,
                available_until=now + timedelta(hours=8),
                current_location=depot,
                status=VehicleStatus.AVAILABLE,
            )
        )

    router = GraphDispatchRouter(urban_road_graph)
    solver = Phase3Solver(router, objective=Objective(ObjectiveConfig()))

    result = solver.solve(orders, vehicles, method="greedy_2opt")

    # ALL 50 orders must be served!
    assert result.unserved_orders == 0
    assert result.served_orders == 50
    # Multiple orders assigned per vehicle
    for route in result.routes:
        assert len(route.order_ids) > 1


def test_metaheuristic_route_optimizers():
    # Tour stops [0, 1, 2, 3, 4]
    stops = ["depot", "stop_1", "stop_2", "stop_3", "stop_4"]

    def sample_cost(seq: list[str]) -> float:
        # Distance penalty for non-alphabetical stop sequences
        indices = [0 if s == "depot" else int(s.split("_")[1]) for s in seq]
        return sum(abs(indices[i] - indices[i + 1]) for i in range(len(indices) - 1))

    scrambled = ["depot", "stop_4", "stop_1", "stop_3", "stop_2"]
    initial_cost = sample_cost(scrambled)

    sa_opt, sa_cost = SimulatedAnnealingSolver(seed=42).optimize(scrambled, sample_cost)
    tabu_opt, tabu_cost = TabuSearchSolver().optimize(scrambled, sample_cost)
    two_opt_res, two_opt_cost = two_opt(scrambled, sample_cost)

    assert sa_cost <= initial_cost
    assert tabu_cost <= initial_cost
    assert two_opt_cost <= initial_cost
