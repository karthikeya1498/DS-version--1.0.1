"""Monotonic Stack algorithms for next greater/smaller element queries."""
from __future__ import annotations

from typing import Any, Sequence


def next_greater_elements(arr: Sequence[Any]) -> list[int]:
    """
    For each index i, find the index of the next strictly greater element to the right.
    Returns -1 if no greater element exists. Runs in O(N) time.
    """
    n = len(arr)
    result = [-1] * n
    stack: list[int] = []  # indices

    for i in range(n):
        while stack and arr[i] > arr[stack[-1]]:
            idx = stack.pop()
            result[idx] = i
        stack.append(i)

    return result


def previous_greater_elements(arr: Sequence[Any]) -> list[int]:
    """
    For each index i, find the index of the previous strictly greater element to the left.
    """
    n = len(arr)
    result = [-1] * n
    stack: list[int] = []

    for i in range(n - 1, -1, -1):
        while stack and arr[i] > arr[stack[-1]]:
            idx = stack.pop()
            result[idx] = i
        stack.append(i)

    return result
