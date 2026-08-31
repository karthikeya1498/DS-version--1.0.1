"""Binary search algorithms for sorted sequences."""
from __future__ import annotations

from typing import Any, Callable, Sequence


def binary_search(arr: Sequence[Any], target: Any, key: Callable[[Any], Any] | None = None) -> int:
    """
    Search for target in sorted sequence arr.
    Returns index of target if found, else -1.
    """
    low, high = 0, len(arr) - 1
    target_val = key(target) if key else target

    while low <= high:
        mid = (low + high) // 2
        mid_val = key(arr[mid]) if key else arr[mid]
        if mid_val == target_val:
            return mid
        elif mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def lower_bound(arr: Sequence[Any], target: Any, key: Callable[[Any], Any] | None = None) -> int:
    """Find the first index where arr[i] >= target (bisect_left)."""
    low, high = 0, len(arr)
    target_val = key(target) if key else target

    while low < high:
        mid = (low + high) // 2
        mid_val = key(arr[mid]) if key else arr[mid]
        if mid_val < target_val:
            low = mid + 1
        else:
            high = mid
    return low


def upper_bound(arr: Sequence[Any], target: Any, key: Callable[[Any], Any] | None = None) -> int:
    """Find the first index where arr[i] > target (bisect_right)."""
    low, high = 0, len(arr)
    target_val = key(target) if key else target

    while low < high:
        mid = (low + high) // 2
        mid_val = key(arr[mid]) if key else arr[mid]
        if mid_val <= target_val:
            low = mid + 1
        else:
            high = mid
    return low
