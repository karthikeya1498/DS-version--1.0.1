"""0/1 and Unbounded Knapsack Dynamic Programming algorithms."""
from __future__ import annotations

from typing import Sequence


def knapsack(weights: Sequence[int], values: Sequence[float], capacity: int) -> tuple[float, list[int]]:
    """
    Solve the 0/1 Knapsack Problem.
    
    Args:
        weights: Integer weights of items.
        values: Values of items.
        capacity: Maximum integer capacity.
        
    Returns:
        (max_value, list_of_selected_indices)
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0.0, []

    for w in weights:
        if w < 0:
            raise ValueError("Weights must be non-negative integers")
    if capacity < 0:
        raise ValueError("Capacity must be non-negative")

    # dp[i][w] stores maximum value achievable using a subset of first i items with capacity w
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = values[i - 1]
        for w in range(capacity + 1):
            if wt <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to find chosen items
    chosen_indices = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen_indices.append(i - 1)
            w -= weights[i - 1]

    chosen_indices.reverse()
    return dp[n][capacity], chosen_indices


def unbounded_knapsack(weights: Sequence[int], values: Sequence[float], capacity: int) -> tuple[float, list[int]]:
    """
    Solve the Unbounded Knapsack Problem (items can be picked multiple times).
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0.0, []

    dp = [0.0] * (capacity + 1)
    best_item = [-1] * (capacity + 1)

    for w in range(1, capacity + 1):
        for i in range(n):
            if weights[i] <= w:
                candidate = dp[w - weights[i]] + values[i]
                if candidate > dp[w]:
                    dp[w] = candidate
                    best_item[w] = i

    # Reconstruct items
    chosen = []
    curr_cap = capacity
    while curr_cap > 0 and best_item[curr_cap] != -1:
        idx = best_item[curr_cap]
        chosen.append(idx)
        curr_cap -= weights[idx]

    return dp[capacity], chosen
