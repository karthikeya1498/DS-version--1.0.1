"""Service level and unserved order penalties."""
from __future__ import annotations


def calculate_unserved_penalty(unserved_count: int, penalty_per_order: float = 50.0) -> float:
    return unserved_count * penalty_per_order
