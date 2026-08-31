"""Deterministic genetic algorithm for closed route permutations."""

from __future__ import annotations

from collections.abc import Callable
from random import Random


def _repair(route: list[str], template: list[str]) -> list[str]:
    start, end = template[0], template[-1]
    interior = []
    for item in route[1:-1]:
        if item not in interior and item not in (start, end):
            interior.append(item)
    interior.extend(item for item in template[1:-1] if item not in interior)
    return [start, *interior, end]


def optimize(
    route: list[str],
    cost: Callable[[list[str]], float],
    seed: int = 42,
    population_size: int = 24,
    generations: int = 40,
    mutation_rate: float = 0.15,
) -> tuple[list[str], float]:
    """Return the best feasible chromosome and its cost using seeded GA search."""
    if len(route) < 4:
        return list(route), cost(route)
    random = Random(seed)
    template = list(route)
    interior = template[1:-1]
    population = [template]
    for _ in range(max(1, population_size - 1)):
        candidate = list(interior)
        random.shuffle(candidate)
        population.append([template[0], *candidate, template[-1]])
    best = min(population, key=cost)
    best_cost = cost(best)
    for _ in range(generations):
        population.sort(key=cost)
        survivors = population[: max(2, population_size // 2)]
        next_population = list(survivors)
        while len(next_population) < population_size:
            left, right = random.sample(survivors, 2)
            cut = random.randrange(1, len(template) - 1)
            prefix = left[:cut]
            child = prefix + [item for item in right[1:-1] if item not in prefix] + [left[-1]]
            child = _repair(child, template)
            if random.random() < mutation_rate:
                first, second = random.sample(range(1, len(child) - 1), 2)
                child[first], child[second] = child[second], child[first]
            next_population.append(child)
        population = next_population
        candidate = min(population, key=cost)
        if cost(candidate) < best_cost:
            best, best_cost = list(candidate), cost(candidate)
    return best, best_cost
