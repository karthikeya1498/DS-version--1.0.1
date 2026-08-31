"""Monotonic Queue data structure for O(1) sliding window min/max."""

from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar

T = TypeVar("T")


class MonotonicQueue(Generic[T]):
    """
    Maintains elements in monotonic decreasing (or increasing) order using a deque.
    Provides O(1) amortized push, pop, and max/min queries.
    """

    def __init__(self, mode: str = "max") -> None:
        self.mode = mode
        self.deque: deque[T] = deque()

    def push(self, val: T) -> None:
        """Push value into queue maintaining monotonic invariant."""
        if self.mode == "max":
            while self.deque and self.deque[-1] < val:
                self.deque.pop()
        else:
            while self.deque and self.deque[-1] > val:
                self.deque.pop()
        self.deque.append(val)

    def pop(self, val: T) -> None:
        """Remove value if it is currently at the front of the queue."""
        if self.deque and self.deque[0] == val:
            self.deque.popleft()

    def extremum(self) -> T:
        """Return current maximum (or minimum) in O(1)."""
        if not self.deque:
            raise IndexError("MonotonicQueue is empty")
        return self.deque[0]

    def max(self) -> T:
        return self.extremum()

    def min(self) -> T:
        return self.extremum()

    def __len__(self) -> int:
        return len(self.deque)
