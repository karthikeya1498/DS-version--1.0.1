"""Sliding window algorithms for streaming logistics metrics."""

from __future__ import annotations

from collections.abc import Sequence

from src.dsa.sequences.monotonic_queue import MonotonicQueue


def sliding_window_max(arr: Sequence[float], k: int) -> list[float]:
    """
    Compute maximum values for all sliding windows of size k in O(N) time.
    """
    if not arr or k <= 0 or k > len(arr):
        return []

    mq = MonotonicQueue[float](mode="max")
    result: list[float] = []

    for i in range(len(arr)):
        mq.push(arr[i])
        if i >= k - 1:
            result.append(mq.max())
            mq.pop(arr[i - k + 1])

    return result


def sliding_window_average(arr: Sequence[float], k: int) -> list[float]:
    """
    Compute moving average for sliding windows of size k in O(N) time.
    """
    if not arr or k <= 0 or k > len(arr):
        return []

    result: list[float] = []
    window_sum = sum(arr[:k])
    result.append(window_sum / k)

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        result.append(window_sum / k)

    return result
