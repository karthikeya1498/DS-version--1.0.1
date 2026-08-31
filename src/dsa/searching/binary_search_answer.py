"""Binary search on answer for monotonic predicates (e.g. minimum feasible fleet size)."""
from __future__ import annotations

from typing import Callable


def binary_search_minimum_feasible(
    low: int,
    high: int,
    predicate: Callable[[int], bool],
) -> int | None:
    """
    Find the minimum integer k in range [low, high] such that predicate(k) is True.
    Assumes monotonicity: if predicate(k) is True, then predicate(k+1) is also True.
    
    Returns None if no value in [low, high] satisfies predicate.
    """
    result = None
    l, r = low, high

    while l <= r:
        mid = (l + r) // 2
        if predicate(mid):
            result = mid
            r = mid - 1  # Try to find a smaller feasible answer
        else:
            l = mid + 1

    return result


def binary_search_maximum_feasible(
    low: int,
    high: int,
    predicate: Callable[[int], bool],
) -> int | None:
    """
    Find the maximum integer k in range [low, high] such that predicate(k) is True.
    Assumes monotonicity: if predicate(k) is True, then predicate(k-1) is also True.
    """
    result = None
    l, r = low, high

    while l <= r:
        mid = (l + r) // 2
        if predicate(mid):
            result = mid
            l = mid + 1  # Try to find a larger feasible answer
        else:
            r = mid - 1

    return result
