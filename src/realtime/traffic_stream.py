"""In-process traffic and route re-optimization event stream."""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Any

class TrafficStream:
    def __init__(self):
        self._subscribers: set[asyncio.Queue] = set()
    async def subscribe(self):
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue
    def unsubscribe(self, queue): self._subscribers.discard(queue)
    async def publish(self, event_type: str, payload: dict[str, Any]):
        event = {'event_type': event_type, 'timestamp': datetime.now(timezone.utc).isoformat(), 'payload': payload}
        for queue in tuple(self._subscribers):
            if queue.full(): queue.get_nowait()
            await queue.put(event)

traffic_stream = TrafficStream()
