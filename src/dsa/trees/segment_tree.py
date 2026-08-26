"""Segment tree for range maximum queries and point updates."""
class SegmentTree:
    def __init__(self, values):
        self.n = len(values); size = 1
        while size < max(1, self.n): size *= 2
        self._size, self._tree = size, [float('-inf')] * (2 * size)
        self._tree[size:size + self.n] = values
        for i in range(size - 1, 0, -1): self._tree[i] = max(self._tree[2*i], self._tree[2*i+1])
    def update(self, index: int, value: float) -> None:
        if not 0 <= index < self.n: raise IndexError(index)
        i = self._size + index; self._tree[i] = value
        while i > 1: i //= 2; self._tree[i] = max(self._tree[2*i], self._tree[2*i+1])
    def query_max(self, left: int, right: int) -> float:
        if not 0 <= left <= right <= self.n: raise IndexError((left, right))
        left += self._size; right += self._size; result = float('-inf')
        while left < right:
            if left & 1: result = max(result, self._tree[left]); left += 1
            if right & 1: right -= 1; result = max(result, self._tree[right])
            left //= 2; right //= 2
        return result
