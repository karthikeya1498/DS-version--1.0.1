"""Stable min-priority queue used by shortest-path algorithms."""

from heapq import heappop, heappush


class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._sequence = 0

    def push(self, priority: float, item: str) -> None:
        heappush(self._heap, (priority, self._sequence, item))
        self._sequence += 1

    def pop(self) -> tuple[float, str]:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        priority, _, item = heappop(self._heap)
        return priority, item

    def __bool__(self):
        return bool(self._heap)

    def __len__(self):
        return len(self._heap)
