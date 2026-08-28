"""In-process traffic and route re-optimization event stream.

Author: Karthikeya
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any


class TrafficStream:
    """Broadcast bounded events to currently connected subscribers."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        """Create and register a bounded queue for one WebSocket client."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove a disconnected client queue."""
        self._subscribers.discard(queue)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        """Broadcast one event with O(subscribers) non-blocking queue writes."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        for queue in tuple(self._subscribers):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(event)


traffic_stream = TrafficStream()
