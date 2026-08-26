"""Hybrid orchestration around greedy graph dispatch and objective scoring."""
from time import perf_counter
from src.common.contracts import OptimizationResult, RoutePlan
from src.optimization.objectives.cost import total_cost
class HybridSolver:
    def __init__(self, router): self.router = router
    def solve(self, orders, vehicles):
        started = perf_counter(); routes=[]; remaining=list(orders)
        for order in list(remaining):
            route = self.router.route(order, vehicles)
            if route:
                routes.append(RoutePlan(route.vehicle_id, (order.order_id,), route.path, route.travel_cost)); remaining.remove(order)
        distance=sum(r.distance_km for r in routes)
        return OptimizationResult(tuple(routes), total_cost(distance, unserved=len(remaining)), sum(len(r.order_ids) for r in routes), len(remaining), (perf_counter()-started)*1000, 'graph_dispatch', {'distance_km': distance})
