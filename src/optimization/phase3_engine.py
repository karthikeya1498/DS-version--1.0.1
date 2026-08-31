"""Phase 3: prediction-aware, capacity-constrained multi-order optimization orchestration."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter

from src.common.contracts import OptimizationResult, RoutePlan
from src.dsa.graphs.astar import shortest_path as astar_path
from src.optimization.assignment.order_assignment import cluster_orders_by_capacity
from src.optimization.constraints.time_windows import calculate_schedule_lateness
from src.optimization.objectives.cost import ObjectiveConfig
from src.optimization.routing.genetic_algorithm import optimize as genetic_optimize
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.optimization.routing.simulated_annealing import SimulatedAnnealingSolver
from src.optimization.routing.tabu_search import TabuSearchSolver
from src.optimization.routing.three_opt import improve as three_opt
from src.optimization.routing.two_opt import improve as two_opt
from src.optimization.solver.ortools_solver import ORToolsRoutingSolver
from src.simulation.models import Order, Vehicle, VehicleStatus


@dataclass(frozen=True)
class ObjectiveWeights:
    distance: float = 1.0
    fuel: float = 1.5
    lateness: float = 5.0
    unserved: float = 50.0
    vehicle_usage: float = 10.0


@dataclass(frozen=True)
class ConstraintReport:
    feasible: bool
    violations: tuple[str, ...] = ()


@dataclass(frozen=True)
class Prediction:
    demand: float
    eta_minutes: float = 0.0
    late_risk: float = 0.0
    uncertainty: float = 0.0


@dataclass(frozen=True)
class DecisionCandidate:
    order: Order
    vehicle: Vehicle
    score: float
    estimated_cost: float
    predicted_lateness: float


@dataclass(frozen=True)
class OptimizationPlan:
    assignments: tuple[tuple[str, str], ...]
    routes: tuple[RoutePlan, ...]
    objective: float
    distance_km: float
    fuel_cost: float
    lateness_minutes: float
    unserved_orders: int
    activated_vehicles: int
    feasible: bool
    violations: tuple[str, ...] = ()


class Objective:
    """Single, shared scalar objective used by every Phase 3 solver."""

    def __init__(
        self,
        weights: ObjectiveWeights | ObjectiveConfig = ObjectiveWeights(),
        fuel_rate: float = 1.5,
    ) -> None:
        if isinstance(weights, ObjectiveConfig):
            self.weights = ObjectiveWeights(
                distance=weights.distance_cost_per_km,
                fuel=weights.fuel_cost_per_km,
                lateness=weights.lateness_cost_per_minute,
                unserved=weights.unserved_order_penalty,
                vehicle_usage=weights.vehicle_activation_cost,
            )
        else:
            self.weights = weights
        self.fuel_rate = fuel_rate

    def score(
        self,
        *,
        distance_km: float,
        lateness_minutes: float = 0.0,
        unserved_orders: int = 0,
        activated_vehicles: int = 0,
        expected_late_risk: float = 0.0,
    ) -> float:
        fuel = distance_km * self.fuel_rate
        return (
            self.weights.distance * distance_km
            + self.weights.fuel * fuel
            + self.weights.lateness * lateness_minutes
            + self.weights.unserved * unserved_orders
            + self.weights.vehicle_usage * activated_vehicles
            + 20.0 * expected_late_risk
        )


class ConstraintEngine:
    """Hard constraints are rejection rules; soft lateness is measured and penalized."""

    def check_order_vehicle(
        self,
        order: Order,
        vehicle: Vehicle,
        timestamp: datetime | None = None,
    ) -> ConstraintReport:
        timestamp = timestamp or order.created_at
        violations = []
        if vehicle.status != VehicleStatus.AVAILABLE:
            violations.append(f"vehicle_unavailable:{vehicle.vehicle_id}")
        if vehicle.load_units + order.demand_units > vehicle.capacity_units:
            violations.append(f"capacity_exceeded:{order.order_id}")
        if not (vehicle.available_from <= timestamp <= vehicle.available_until):
            violations.append(f"vehicle_shift:{vehicle.vehicle_id}")
        return ConstraintReport(not violations, tuple(violations))

    def check_route(
        self,
        route: RoutePlan,
        orders: Iterable[Order],
        vehicles: Iterable[Vehicle],
    ) -> ConstraintReport:
        violations = list(route.violations)
        order_map = {o.order_id: o for o in orders}
        vehicle_map = {v.vehicle_id: v for v in vehicles}
        vehicle = vehicle_map.get(route.vehicle_id)
        if vehicle is None:
            violations.append(f"unknown_vehicle:{route.vehicle_id}")
        else:
            load = sum(order_map[i].demand_units for i in route.order_ids if i in order_map)
            if load > vehicle.capacity_units:
                violations.append(f"capacity_exceeded:{route.vehicle_id}")
        for order_id in route.order_ids:
            if order_id not in order_map:
                violations.append(f"unknown_order:{order_id}")
        return ConstraintReport(not violations, tuple(violations))


def select_capacity_subset(
    items: list[tuple[str, int, float]],
    capacity: int,
) -> tuple[str, ...]:
    """0/1 knapsack DP for selecting highest-value orders within vehicle capacity."""
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    dp = [0.0] * (capacity + 1)
    chosen: list[tuple[str, int, int]] = []
    for index, (item_id, weight, value) in enumerate(items):
        if weight <= 0:
            raise ValueError("item weight must be positive")
        for cap in range(capacity, weight - 1, -1):
            candidate = dp[cap - weight] + value
            dp[cap] = max(dp[cap], candidate)
    cap = capacity
    for index in range(len(items) - 1, -1, -1):
        item_id, weight, value = items[index]
        previous = dp[cap - weight] + value if cap >= weight else -1.0
        if cap >= weight and abs(dp[cap] - previous) < 1e-9:
            chosen.append((item_id, weight, index))
            cap -= weight
    return tuple(item_id for item_id, _, _ in reversed(chosen))


def minimum_feasible(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Binary search the minimum k for a monotonic fleet-feasibility predicate."""
    answer = None
    while low <= high:
        mid = (low + high) // 2
        if predicate(mid):
            answer, high = mid, mid - 1
        else:
            low = mid + 1
    return answer


def optimize_sequence(
    sequence: list[str],
    cost: Callable[[list[str]], float],
    method: str = "greedy_2opt",
    seed: int = 42,
) -> tuple[list[str], float]:
    """Apply a comparable route-order improvement operator to one vehicle sequence."""
    if method == "greedy":
        return list(sequence), cost(sequence)
    if method in {"greedy_2opt", "2opt"}:
        return two_opt(sequence, cost)
    if method in {"greedy_3opt", "3opt"}:
        return three_opt(sequence, cost)
    if method == "simulated_annealing":
        return SimulatedAnnealingSolver(seed=seed).optimize(sequence, cost)
    if method == "tabu_search":
        return TabuSearchSolver().optimize(sequence, cost)
    if method == "genetic":
        return genetic_optimize(sequence, cost, seed=seed)
    if method == "ortools":
        # Calculate full distance matrix for sequence
        n = len(sequence)
        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_matrix[i][j] = cost([sequence[i], sequence[j]])
        return ORToolsRoutingSolver().solve_tsp(sequence, dist_matrix)
    return two_opt(sequence, cost)


class Phase3Solver:
    """
    Unified Capacity-Constrained Vehicle Routing Problem (CVRP) solver.
    Orchestrates multi-order capacity bundling, multi-stop tour sequencing,
    and objective optimization.
    """

    def __init__(
        self,
        router: GraphDispatchRouter,
        objective: Objective | None = None,
    ) -> None:
        self.router = router
        self.graph = router.graph
        self.objective = objective or Objective()
        self.constraints = ConstraintEngine()

    def _shortest_path_cost(self, u: str, v: str) -> tuple[float, tuple[str, ...]]:
        if u == v:
            return 0.0, (u,)
        res = astar_path(self.graph, u, v)
        if res is not None:
            return res.cost, res.path
        # Fallback Euclidean
        node_u, node_v = self.graph.nodes.get(u), self.graph.nodes.get(v)
        if node_u and node_v:
            d = (
                math.sqrt(
                    (node_u.latitude - node_v.latitude) ** 2
                    + (node_u.longitude - node_v.longitude) ** 2
                )
                * 111.0
            )
            return d, (u, v)
        return 10.0, (u, v)

    def solve(
        self,
        orders: list[Order],
        vehicles: list[Vehicle],
        predictions: dict[str, Prediction] | None = None,
        method: str = "greedy_2opt",
    ) -> OptimizationResult:
        started = perf_counter()
        predictions = predictions or {}

        if not orders or not vehicles:
            return OptimizationResult(
                (),
                self.objective.score(
                    distance_km=0, lateness_minutes=0, unserved_orders=len(orders)
                ),
                0,
                len(orders),
                (perf_counter() - started) * 1000,
                method,
                {"distance_km": 0.0, "activated_vehicles": 0.0, "lateness_minutes": 0.0},
            )

        # 1. Capacity-Aware Multi-Order Clustering (Bin-Packing)
        bundles, unserved_orders_list = cluster_orders_by_capacity(orders, vehicles)

        route_plans: list[RoutePlan] = []
        total_distance = 0.0
        total_lateness = 0.0
        activated_vehicles = set()
        vehicle_map = {v.vehicle_id: v for v in vehicles}

        for v_id, bundle_orders in bundles.items():
            if not bundle_orders:
                continue

            vehicle = vehicle_map[v_id]
            activated_vehicles.add(v_id)
            v_start_node = vehicle.current_location.node_id

            order_dest_nodes = [o.destination.node_id for o in bundle_orders]
            stop_nodes = [v_start_node] + order_dest_nodes

            # Tour cost evaluation closure
            def tour_cost(nodes: list[str]) -> float:
                cost = 0.0
                for u, v in zip(nodes[:-1], nodes[1:]):
                    d, _ = self._shortest_path_cost(u, v)
                    cost += d
                return cost

            # 2. Multi-Stop Sequence Optimization
            optimized_nodes, tour_dist = optimize_sequence(stop_nodes, tour_cost, method=method)

            # Map optimized stop nodes back to order sequence
            node_to_order = {o.destination.node_id: o for o in bundle_orders}
            ordered_orders = [
                node_to_order[n_id] for n_id in optimized_nodes[1:] if n_id in node_to_order
            ]
            # In case of duplicate destination nodes, include any missing orders from bundle
            for o in bundle_orders:
                if o not in ordered_orders:
                    ordered_orders.append(o)

            # 3. Assemble full path across stops
            full_path: list[str] = [v_start_node]
            segment_times_min: list[float] = []

            for u, v in zip(optimized_nodes[:-1], optimized_nodes[1:]):
                d, path = self._shortest_path_cost(u, v)
                full_path.extend(path[1:])
                # Speed approx 40 km/h -> time = (d / 40) * 60 min
                segment_times_min.append(max(1.0, (d / 40.0) * 60.0))

            # 4. Schedule Lateness & Arrival Simulation
            start_time = bundle_orders[0].created_at
            lateness_min, _, _ = calculate_schedule_lateness(
                ordered_orders, start_time, segment_times_min
            )

            total_distance += tour_dist
            total_lateness += lateness_min

            ordered_order_ids = tuple(o.order_id for o in ordered_orders)
            route_plans.append(
                RoutePlan(
                    vehicle_id=v_id,
                    order_ids=ordered_order_ids,
                    node_path=tuple(full_path),
                    distance_km=tour_dist,
                    lateness_minutes=lateness_min,
                )
            )

        unserved_count = len(unserved_orders_list)
        served_count = len(orders) - unserved_count

        total_obj = self.objective.score(
            distance_km=total_distance,
            lateness_minutes=total_lateness,
            unserved_orders=unserved_count,
            activated_vehicles=len(activated_vehicles),
        )

        runtime_ms = (perf_counter() - started) * 1000

        return OptimizationResult(
            routes=tuple(route_plans),
            total_cost=total_obj,
            served_orders=served_count,
            unserved_orders=unserved_count,
            runtime_ms=runtime_ms,
            strategy=method,
            diagnostics={
                "distance_km": total_distance,
                "activated_vehicles": float(len(activated_vehicles)),
                "lateness_minutes": total_lateness,
            },
        )

    def optimize_sequence(
        self,
        sequence: list[str],
        cost: Callable[[list[str]], float],
        method: str = "greedy_2opt",
        seed: int = 42,
    ) -> tuple[list[str], float]:
        return optimize_sequence(sequence, cost, method, seed)
