"""Segment tree for range queries (max, min, sum) and point updates in O(log N)."""

from __future__ import annotations

from collections.abc import Callable, Sequence


class SegmentTree:
    def __init__(
        self,
        values: Sequence[float],
        combine: Callable[[float, float], float] = max,
        default_val: float | None = None,
    ):
        self.n = len(values)
        self.combine = combine
        if default_val is not None:
            self.default_val = default_val
        elif combine == min:
            self.default_val = float("inf")
        elif combine == max:
            self.default_val = float("-inf")
        else:
            self.default_val = 0.0

        size = 1
        while size < max(1, self.n):
            size *= 2
        self._size = size
        self._tree = [self.default_val] * (2 * size)
        for idx, v in enumerate(values):
            self._tree[size + idx] = float(v)

        for i in range(size - 1, 0, -1):
            self._tree[i] = self.combine(self._tree[2 * i], self._tree[2 * i + 1])

    def update(self, index: int, value: float) -> None:
        """Point update value at index in O(log N)."""
        if not 0 <= index < self.n:
            raise IndexError(index)
        i = self._size + index
        self._tree[i] = float(value)
        while i > 1:
            i //= 2
            self._tree[i] = self.combine(self._tree[2 * i], self._tree[2 * i + 1])

    def query(self, left: int, right: int) -> float:
        """
        Query range [left, right] inclusive in O(log N).
        """
        if not 0 <= left <= right < self.n:
            raise IndexError((left, right))
        return self._query_internal(left, right + 1)

    def _query_internal(self, left: int, right: int) -> float:
        """Half-open query [left, right)."""
        l = left + self._size
        r = right + self._size
        result = self.default_val
        while l < r:
            if l & 1:
                result = self.combine(result, self._tree[l])
                l += 1
            if r & 1:
                r -= 1
                result = self.combine(result, self._tree[r])
            l //= 2
            r //= 2
        return result

    def query_max(self, left: int, right: int) -> float:
        """Backwards-compatible half-open query_max(left, right) in [left, right)."""
        if not 0 <= left <= right <= self.n:
            raise IndexError((left, right))
        return self._query_internal(left, right)
