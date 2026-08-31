"""Resource Allocation Dynamic Programming algorithm for fleet and warehouse capacity."""

from __future__ import annotations

from collections.abc import Callable


def allocate_resources(
    num_resources: int,
    projects_count: int,
    return_fn: Callable[[int, int], float],
) -> tuple[float, list[int]]:
    """
    Allocate `num_resources` units across `projects_count` entities (e.g. vehicles to zones)
    to maximize total return.

    Args:
        num_resources: Total available discrete units (e.g. 10 vehicles).
        projects_count: Number of targets (e.g. 4 logistics delivery zones).
        return_fn(project_idx, allocated_units) -> utility/return.

    Returns:
        (max_return, allocation_list_per_project)
    """
    if num_resources < 0 or projects_count <= 0:
        return 0.0, [0] * projects_count

    # dp[i][r]: max return allocating r resources to first i projects
    dp = [[0.0] * (num_resources + 1) for _ in range(projects_count + 1)]
    choice = [[0] * (num_resources + 1) for _ in range(projects_count + 1)]

    for i in range(1, projects_count + 1):
        for r in range(num_resources + 1):
            best_val = -float("inf")
            best_k = 0
            for k in range(r + 1):
                gain = return_fn(i - 1, k) + dp[i - 1][r - k]
                if gain > best_val:
                    best_val = gain
                    best_k = k
            dp[i][r] = best_val
            choice[i][r] = best_k

    # Backtrack allocation
    allocations = [0] * projects_count
    curr_r = num_resources
    for i in range(projects_count, 0, -1):
        k = choice[i][curr_r]
        allocations[i - 1] = k
        curr_r -= k

    return dp[projects_count][num_resources], allocations
