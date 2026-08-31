"""Simple max heap abstraction."""

import heapq


class MaxHeap:
    def __init__(self):
        self._heap = []

    def push(self, value):
        heapq.heappush(self._heap, -value)

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty max heap")
        return -heapq.heappop(self._heap)
