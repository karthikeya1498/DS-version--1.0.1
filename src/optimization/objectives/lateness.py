"""Lateness cost and SLA breach penalty."""

from __future__ import annotations


def calculate_lateness_penalty(lateness_minutes: float, cost_per_minute: float = 5.0) -> float:
    return max(0.0, lateness_minutes) * cost_per_minute
