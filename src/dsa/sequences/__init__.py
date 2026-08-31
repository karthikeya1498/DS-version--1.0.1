"""Sequences and monotonic data structures package."""
from src.dsa.sequences.monotonic_queue import MonotonicQueue
from src.dsa.sequences.monotonic_stack import next_greater_elements, previous_greater_elements
from src.dsa.sequences.sliding_window import sliding_window_average, sliding_window_max

__all__ = [
    "MonotonicQueue",
    "next_greater_elements",
    "previous_greater_elements",
    "sliding_window_max",
    "sliding_window_average",
]
