"""Phase 3: prediction-aware, constraint-safe optimization orchestration."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from heapq import heappop, heappush
from math import exp
from random import Random
from time import perf_counter

from src.common.contracts import OptimizationResult, RoutePlan
from src.optimization.routing.genetic_algorithm import optimize as genetic_optimize
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.optimization.routing.three_opt import improve as three_opt
from src.optimization.routing.two_opt import improve as two_opt
from src.simulation.models import Order, OrderStatus, Vehicle, VehicleStatus


@dataclass(frozen=True)
class ObjectiveWeights:
    distance: float = 1.0
    fuel: float = 1.5
    lateness: float = 10.0
    unserved: float = 100.0
    vehicle_usage: float = 5.0


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

    def __init__(self, weights: ObjectiveWeights = ObjectiveWeights(), fuel_rate: float = 1.0) -> None:
        self.weights, self.fuel_rate = weights, fuel_rate

    def score(self, *, distance_km: float, lateness_minutes: float = 0.0,
              unserved_orders: int = 0, activated_vehicles: int = 0) -> float:
        fuel = distance_km * self.fuel_rate
        return (self.weights.distance * distance_km + self.weights.fuel * fuel
                + self.weights.lateness * lateness_minutes
                + self.weights.unserved * unserved_orders
                + self.weights.vehicle_usage * activated_vehicles)


class ConstraintEngine:
    """Hard constraints are rejection rules; soft lateness is measured, not hidden."""

    def check_order_vehicle(self, order: Order, vehicle: Vehicle, timestamp=None) -> ConstraintReport:
        timestamp = timestamp or order.created_at
        violations = []
        if vehicle.status != VehicleStatus.AVAILABLE: violations.append(f"vehicle_unavailable:{vehicle.vehicle_id}")
        if vehicle.load_units + order.demand_units > vehicle.capacity_units: violations.append(f"capacity_exceeded:{order.order_id}")
        if not vehicle.available_from <= timestamp <= vehicle.available_until: violations.append(f"vehicle_shift:{vehicle.vehicle_id}")
        return ConstraintReport(not violations, tuple(violations))

    def check_route(self, route: RoutePlan, orders: Iterable[Order], vehicles: Iterable[Vehicle]) -> ConstraintReport:
        violations = list(route.violations)
        order_map, vehicle_map = {o.order_id: o for o in orders}, {v.vehicle_id: v for v in vehicles}
        vehicle = vehicle_map.get(route.vehicle_id)
        if vehicle is None: violations.append(f"unknown_vehicle:{route.vehicle_id}")
        else:
            load = sum(order_map[i].demand_units for i in route.order_ids if i in order_map)
            if load > vehicle.capacity_units: violations.append(f"capacity_exceeded:{route.vehicle_id}")
        for order_id in route.order_ids:
            if order_id not in order_map: violations.append(f"unknown_order:{order_id}")
        return ConstraintReport(not violations, tuple(violations))


def select_capacity_subset(items: list[tuple[str, int, float]], capacity: int) -> tuple[str, ...]:
    """0/1 knapsack DP for selecting highest-value orders within vehicle capacity."""
    if capacity < 0: raise ValueError("capacity must be non-negative")
    dp = [0.0] * (capacity + 1); chosen: list[tuple[str, int, int]] = []
    for index, (item_id, weight, value) in enumerate(items):
        if weight <= 0: raise ValueError("item weight must be positive")
        for cap in range(capacity, weight - 1, -1):
            candidate = dp[cap - weight] + value
            dp[cap] = max(dp[cap], candidate)
    cap = capacity
    for index in range(len(items) - 1, -1, -1):
        item_id, weight, value = items[index]
        previous = dp[cap - weight] + value if cap >= weight else -1.0
        if cap >= weight and abs(dp[cap] - previous) < 1e-9:
            chosen.append((item_id, weight, index)); cap -= weight
    return tuple(item_id for item_id, _, _ in reversed(chosen))


def minimum_feasible(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Binary search the minimum k for a monotonic fleet-feasibility predicate."""
    answer = None
    while low <= high:
        mid = (low + high) // 2
        if predicate(mid): answer, high = mid, mid - 1
        else: low = mid + 1
    return answer


class GreedyAssignmentSolver:
    """Priority-queue assignment baseline; deterministic under equal scores."""

    def __init__(self, router: GraphDispatchRouter, objective: Objective | None = None,
                 constraints: ConstraintEngine | None = None) -> None:
        self.router, self.objective = router, objective or Objective(); self.constraints = constraints or ConstraintEngine()

    def solve(self, orders: list[Order], vehicles: list[Vehicle], predictions: dict[str, Prediction] | None = None,
              strategy: str = "greedy") -> OptimizationResult:
        started = perf_counter(); predictions = predictions or {}; heap = []
        for order in orders:
            prediction = predictions.get(order.order_id, Prediction(order.demand_units))
            heappush(heap, (-order.priority, prediction.late_risk, order.created_at.timestamp(), order.order_id, order))
        routes, unserved, used = [], 0, set()
        while heap:
            _, _, _, _, order = heappop(heap); candidates: list[DecisionCandidate] = []
            for vehicle in vehicles:
                report = self.constraints.check_order_vehicle(order, vehicle)
                if not report.feasible: continue
                route = self.router.route(order, [vehicle])
                if route is None: continue
                prediction = predictions.get(order.order_id, Prediction(order.demand_units))
                score = route.travel_cost + (prediction.late_risk + prediction.uncertainty) * self.objective.weights.lateness
                candidates.append(DecisionCandidate(order, vehicle, score, route.travel_cost, prediction.eta_minutes))
                vehicle.status = VehicleStatus.AVAILABLE
                vehicle.load_units -= order.demand_units
                order.status, order.assigned_vehicle_id = OrderStatus.PENDING, None
            if not candidates: unserved += 1; continue
            chosen = min(candidates, key=lambda c: (c.score, c.vehicle.vehicle_id)); route = self.router.route(order, [chosen.vehicle])
            assert route is not None
            routes.append(RoutePlan(route.vehicle_id, (order.order_id,), route.path, route.travel_cost, chosen.predicted_lateness))
            used.add(route.vehicle_id)
        distance = sum(route.distance_km for route in routes); lateness = sum(route.lateness_minutes for route in routes)
        result = OptimizationResult(tuple(routes), self.objective.score(distance_km=distance, lateness_minutes=lateness, unserved_orders=unserved, activated_vehicles=len(used)), len(routes), unserved, (perf_counter() - started) * 1000, strategy, {"distance_km": distance, "activated_vehicles": float(len(used)), "lateness_minutes": lateness})
        return result


class SimulatedAnnealingSolver:
    """Route-order local search with deterministic seeded acceptance schedule."""

    def __init__(self, seed: int = 42, initial_temperature: float = 10.0, cooling: float = .95, iterations: int = 250) -> None:
        self.random = Random(seed); self.initial_temperature, self.cooling, self.iterations = initial_temperature, cooling, iterations

    def optimize(self, route: list[str], cost: Callable[[list[str]], float]) -> tuple[list[str], float]:
        current, current_cost, best, best_cost = list(route), cost(route), list(route), cost(route); temperature = self.initial_temperature
        for _ in range(self.iterations):
            if len(current) < 4: break
            left, right = sorted(self.random.sample(range(1, len(current)), 2)); candidate = current[:left] + current[left:right][::-1] + current[right:]; value = cost(candidate); delta = value - current_cost
            if delta <= 0 or self.random.random() < exp(-delta / max(temperature, 1e-9)): current, current_cost = candidate, value
            if current_cost < best_cost: best, best_cost = list(current), current_cost
            temperature *= self.cooling
        return best, best_cost


def optimize_sequence(sequence: list[str], cost: Callable[[list[str]], float], method: str = 'greedy_2opt', seed: int = 42) -> tuple[list[str], float]:
    """Apply a comparable route-order improvement operator to one vehicle sequence."""
    if method == 'greedy': return list(sequence), cost(sequence)
    if method == 'greedy_2opt': return two_opt(sequence, cost)
    if method == 'greedy_3opt': return three_opt(sequence, cost)
    if method == 'simulated_annealing': return SimulatedAnnealingSolver(seed=seed).optimize(sequence, cost)
    if method == 'genetic': return genetic_optimize(sequence, cost, seed=seed)
    raise ValueError(f'unsupported route method: {method}')


class Phase3Solver:
    """Unified solver interface used for comparable algorithm experiments."""

    def __init__(self, router: GraphDispatchRouter, objective: Objective | None = None) -> None:
        self.router, self.objective = router, objective or Objective(); self.greedy = GreedyAssignmentSolver(router, self.objective)

    def solve(self, orders: list[Order], vehicles: list[Vehicle], predictions: dict[str, Prediction] | None = None, method: str = "greedy") -> OptimizationResult:
        if method not in {"greedy", "greedy_2opt", "greedy_3opt", "simulated_annealing", "genetic"}: raise ValueError(f"unsupported Phase 3 method: {method}")
        return self.greedy.solve(orders, vehicles, predictions, method)

    def optimize_sequence(self, sequence: list[str], cost: Callable[[list[str]], float], method: str = 'greedy_2opt', seed: int = 42) -> tuple[list[str], float]:
        return optimize_sequence(sequence, cost, method, seed)
