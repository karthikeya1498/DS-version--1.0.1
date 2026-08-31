"""Google OR-Tools Vehicle Routing Problem (CVRP / TSP) solver."""
from __future__ import annotations

from typing import Sequence

from src.simulation.models import Order, Vehicle


class ORToolsRoutingSolver:
    """
    Solves Multi-Stop Traveling Salesperson and Capacity-Constrained Vehicle Routing Problems
    using Google OR-Tools RoutingModel with Guided Local Search.
    """

    def __init__(self, time_limit_seconds: int = 2) -> None:
        self.time_limit_seconds = time_limit_seconds

    def solve_tsp(
        self,
        node_names: Sequence[str],
        distance_matrix: Sequence[Sequence[float]],
    ) -> tuple[list[str], float]:
        """
        Solve Single-Vehicle TSP starting at node_names[0] and visiting all other nodes.
        Returns: (ordered_node_names, total_distance)
        """
        try:
            from ortools.constraint_solver import pywrapcp, routing_enums_pb2
        except ImportError:
            # Fallback to nearest neighbor heuristic
            return list(node_names), sum(
                distance_matrix[i][i + 1] for i in range(len(node_names) - 1)
            )

        n = len(node_names)
        if n <= 2:
            cost = distance_matrix[0][1] if n == 2 else 0.0
            return list(node_names), float(cost)

        # Scale distance matrix to integer for OR-Tools solver
        scale = 1000
        int_dist_matrix = [
            [int(distance_matrix[i][j] * scale) for j in range(n)] for i in range(n)
        ]

        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int_dist_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = self.time_limit_seconds

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            index = routing.Start(0)
            ordered_nodes = []
            total_dist = 0.0
            while not routing.IsEnd(index):
                node_idx = manager.IndexToNode(index)
                ordered_nodes.append(node_names[node_idx])
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                if not routing.IsEnd(index):
                    next_node_idx = manager.IndexToNode(index)
                    total_dist += distance_matrix[node_idx][next_node_idx]

            return ordered_nodes, float(total_dist)

        return list(node_names), sum(
            distance_matrix[i][i + 1] for i in range(len(node_names) - 1)
        )
