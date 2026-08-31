"""Weighted Interval Scheduling Dynamic Programming algorithm."""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Interval:
    id: str
    start: float
    end: float
    weight: float


def weighted_interval_scheduling(intervals: Sequence[Interval]) -> tuple[float, list[Interval]]:
    """
    Find the subset of mutually compatible intervals that maximizes total weight.
    Useful for optimal vehicle driver shift allocation and delivery time window scheduling.
    Runs in O(N log N) time.
    """
    if not intervals:
        return 0.0, []

    # Sort intervals by finish time
    sorted_intervals = sorted(intervals, key=lambda x: x.end)
    n = len(sorted_intervals)
    finish_times = [it.end for it in sorted_intervals]

    # p[i] = largest index j < i such that interval j is compatible with interval i
    p = [0] * n
    for i in range(n):
        # find index where finish_times[j] <= sorted_intervals[i].start
        idx = bisect_right(finish_times, sorted_intervals[i].start) - 1
        p[i] = idx

    # dp[i] = max weight achievable with first i intervals (1-indexed)
    dp = [0.0] * (n + 1)
    for i in range(1, n + 1):
        incl = sorted_intervals[i - 1].weight + (dp[p[i - 1] + 1] if p[i - 1] != -1 else 0.0)
        excl = dp[i - 1]
        dp[i] = max(incl, excl)

    # Backtrack to find chosen intervals
    chosen = []
    curr = n
    while curr > 0:
        incl = sorted_intervals[curr - 1].weight + (dp[p[curr - 1] + 1] if p[curr - 1] != -1 else 0.0)
        excl = dp[curr - 1]
        if incl >= excl:
            chosen.append(sorted_intervals[curr - 1])
            curr = p[curr - 1] + 1 if p[curr - 1] != -1 else 0
        else:
            curr -= 1

    chosen.reverse()
    return dp[n], chosen
