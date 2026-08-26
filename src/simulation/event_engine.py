"""Stable priority-queue event engine."""
from __future__ import annotations
from heapq import heappop, heappush
from collections.abc import Callable
from src.simulation.models import EventType, SimulationEvent

class EventEngine:
    def __init__(self) -> None:
        self._queue: list[SimulationEvent] = []
        self._sequence = 0
        self.processed: list[SimulationEvent] = []

    def schedule(self, timestamp, event_type: EventType, entity_id: str, payload: dict | None = None) -> SimulationEvent:
        event = SimulationEvent(timestamp, self._sequence, event_type, entity_id, payload or {})
        self._sequence += 1
        heappush(self._queue, event)
        return event

    def run(self, handler: Callable[[SimulationEvent], None]) -> list[SimulationEvent]:
        while self._queue:
            event = heappop(self._queue)
            handler(event)
            self.processed.append(event)
        return list(self.processed)
