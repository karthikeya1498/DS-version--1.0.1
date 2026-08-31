"""Simulated Annealing metaheuristic for multi-stop vehicle route sequencing."""
from __future__ import annotations

import math
from random import Random
from typing import Callable, Sequence


class SimulatedAnnealingSolver:
    """
    Simulated Annealing route optimizer with geometric cooling schedule
    and Boltzmann acceptance criterion for escaping local optima.
    """

    def __init__(
        self,
        seed: int = 42,
        initial_temperature: float = 20.0,
        cooling_rate: float = 0.95,
        iterations: int = 300,
    ) -> None:
        self.random = Random(seed)
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.iterations = iterations

    def optimize(
        self,
        route: Sequence[str],
        cost_fn: Callable[[list[str]], float],
    ) -> tuple[list[str], float]:
        """
        Optimize route stop sequence (preserves fixed endpoints).
        """
        current = list(route)
        if len(current) <= 3:
            return current, cost_fn(current)

        current_cost = cost_fn(current)
        best = list(current)
        best_cost = current_cost
        temperature = self.initial_temperature

        # If it's a closed loop (starts and ends at depot), don't touch end index
        max_idx = len(current) - 1 if current[0] == current[-1] else len(current)

        for _ in range(self.iterations):
            if max_idx - 1 < 2:
                break
            i, j = sorted(self.random.sample(range(1, max_idx), 2))
            candidate = current[:i] + current[i : j + 1][::-1] + current[j + 1 :]
            candidate_cost = cost_fn(candidate)

            delta = candidate_cost - current_cost

            if delta < 0 or self.random.random() < math.exp(-delta / max(temperature, 1e-8)):
                current = candidate
                current_cost = candidate_cost

                if current_cost < best_cost:
                    best = list(current)
                    best_cost = current_cost

            temperature *= self.cooling_rate

        return best, best_cost
