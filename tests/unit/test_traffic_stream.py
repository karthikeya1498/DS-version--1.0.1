"""Unit tests for bounded traffic-stream fan-out.

Author: Karthikeya
"""

import asyncio

from src.realtime.traffic_stream import TrafficStream


def test_publish_keeps_latest_event_when_queue_is_full():
    """A slow subscriber loses the oldest event, never the newest event."""

    async def scenario():
        stream = TrafficStream()
        queue = await stream.subscribe()
        for index in range(101):
            await stream.publish("traffic", {"sequence": index})
        events = [queue.get_nowait() for _ in range(queue.qsize())]
        return events

    events = asyncio.run(scenario())
    assert len(events) == 100
    assert events[0]["payload"]["sequence"] == 1
    assert events[-1]["payload"]["sequence"] == 100
