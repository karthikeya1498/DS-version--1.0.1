"""Tabu Search metaheuristic for multi-stop vehicle route sequencing."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Sequence


class TabuSearchSolver:
    """
    Tabu Search local search optimizer with short-term tabu memory
    and aspiration criterion for combinatorial route sequencing.
    """

    def __init__(
        self,
        tabu_tenure: int = 10,
        max_iterations: int = 200,
    ) -> None:
        self.tabu_tenure = tabu_tenure
        self.max_iterations = max_iterations

    def optimize(
        self,
        route: Sequence[str],
        cost_fn: Callable[[list[str]], float],
    ) -> tuple[list[str], float]:
        """Optimize route sequence avoiding recently explored 2-opt transitions."""
        current = list(route)
        if len(current) <= 3:
            return current, cost_fn(current)

        best = list(current)
        best_cost = cost_fn(best)
        current_cost = best_cost

        # Tabu list of forbidden 2-opt swap pairs (i, j)
        tabu_queue: deque[tuple[int, int]] = deque(maxlen=self.tabu_tenure)
        tabu_set: set[tuple[int, int]] = set()

        n = len(current)

        for _ in range(self.max_iterations):
            best_neighbor = None
            best_neighbor_cost = float("inf")
            best_move = None

            # Generate neighborhood moves
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    move = (i, j)
                    candidate = current[:i] + current[i : j + 1][::-1] + current[j + 1 :]
                    c_cost = cost_fn(candidate)

                    # Aspiration criterion: allow tabu move if it strictly improves global best
                    is_tabu = move in tabu_set
                    if not is_tabu or c_cost < best_cost:
                        if c_cost < best_neighbor_cost:
                            best_neighbor = candidate
                            best_neighbor_cost = c_cost
                            best_move = move

            if best_neighbor is None:
                break

            current = best_neighbor
            current_cost = best_neighbor_cost

            if best_move is not None:
                if len(tabu_queue) == self.tabu_tenure:
                    old_move = tabu_queue.popleft()
                    tabu_set.discard(old_move)
                tabu_queue.append(best_move)
                tabu_set.add(best_move)

            if current_cost < best_cost:
                best = list(current)
                best_cost = current_cost

        return best, best_cost
