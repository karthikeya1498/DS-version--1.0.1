"""Fenwick tree supporting point updates and prefix sums in O(log n)."""


class FenwickTree:
    def __init__(self, size: int):
        if size < 0:
            raise ValueError("size must be non-negative")
        self._tree = [0.0] * (size + 1)

    def add(self, index: int, value: float) -> None:
        if not 0 <= index < len(self._tree) - 1:
            raise IndexError(index)
        i = index + 1
        while i < len(self._tree):
            self._tree[i] += value
            i += i & -i

    def prefix_sum(self, end: int) -> float:
        if not 0 <= end <= len(self._tree) - 1:
            raise IndexError(end)
        total, i = 0.0, end
        while i:
            total += self._tree[i]
            i -= i & -i
        return total

    def range_sum(self, start: int, end: int) -> float:
        return self.prefix_sum(end) - self.prefix_sum(start)
