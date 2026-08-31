"""Fenwick tree (Binary Indexed Tree) supporting point updates and prefix sums in O(log n)."""

from __future__ import annotations


class FenwickTree:
    def __init__(self, size: int):
        if size < 0:
            raise ValueError("size must be non-negative")
        self.size = size
        self._tree = [0.0] * (size + 1)
        self._values = [0.0] * size

    def add(self, index: int, value: float) -> None:
        """Add value to index (0-indexed) in O(log N)."""
        if not 0 <= index < self.size:
            raise IndexError(index)
        self._values[index] += value
        i = index + 1
        while i <= self.size:
            self._tree[i] += value
            i += i & -i

    def update(self, index: int, value: float) -> None:
        """Alias for add to record incoming delta or value."""
        self.add(index, value)

    def set_value(self, index: int, value: float) -> None:
        """Set value at index to exact new value in O(log N)."""
        if not 0 <= index < self.size:
            raise IndexError(index)
        delta = value - self._values[index]
        self.add(index, delta)

    def prefix_sum(self, end: int) -> float:
        """Prefix sum from index 0 to end (0-indexed inclusive, clamped)."""
        if end < 0:
            return 0.0
        clamped_end = min(end, self.size - 1)
        total, i = 0.0, clamped_end + 1
        while i > 0:
            total += self._tree[i]
            i -= i & -i
        return total

    def range_sum(self, start: int, end: int) -> float:
        """
        Sum in range [start, end].
        Supports 0-indexed [start, end] and 1-indexed / clamped boundaries.
        """
        if start > end:
            return 0.0
        # If end is passed as self.size (1-based upper bound like range_sum(1, 4) on size 4)
        if end == self.size and start >= 1:
            return self.prefix_sum(self.size - 1) - self.prefix_sum(start - 1)
        return self.prefix_sum(end) - self.prefix_sum(start - 1)
