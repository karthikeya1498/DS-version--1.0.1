"""Sliding-window in-memory rate limiter keyed by tenant."""

from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request


class TenantRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit, self.window_seconds = limit, window_seconds
        self._events = defaultdict(deque)

    def check(self, tenant_id: str) -> None:
        now = monotonic()
        events = self._events[tenant_id]
        while events and events[0] <= now - self.window_seconds:
            events.popleft()
        if len(events) >= self.limit:
            raise HTTPException(status_code=429, detail="rate limit exceeded")
        events.append(now)


limiter = TenantRateLimiter()


async def rate_limit_request(request: Request):
    tenant = getattr(
        request.state, "tenant_id", request.client.host if request.client else "unknown"
    )
    limiter.check(tenant)
