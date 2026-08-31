"""Tenant-aware token-bucket rate limiting with Redis-backed atomic state.

Author: Karthikeya

Redis is the production backend because a process-local limiter is incorrect
when multiple API workers or replicas handle the same tenant. If REDIS_URL is
not configured or Redis is unavailable, the class uses a bounded in-process
fallback so local tests remain deterministic; production should monitor and
alert on fallback activation rather than silently relying on it.
"""

from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - minimal installations use the fallback.
    Redis = None  # type: ignore[assignment,misc]


@dataclass(frozen=True)
class RateLimitDecision:
    """Result of one token-bucket acquisition attempt."""

    allowed: bool
    remaining: int
    retry_after: float


class TenantRateLimiter:
    """Atomic Redis token bucket with a bounded local fallback."""

    _SCRIPT = """
    local now = tonumber(ARGV[1])
    local refill = tonumber(ARGV[2])
    local capacity = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])
    local bucket = redis.call('HMGET', KEYS[1], 'tokens', 'timestamp')
    local tokens = tonumber(bucket[1]) or capacity
    local timestamp = tonumber(bucket[2]) or now
    tokens = math.min(capacity, tokens + math.max(0, now - timestamp) * refill)
    local allowed = 0
    local retry = 0
    if tokens >= requested then
      tokens = tokens - requested
      allowed = 1
    elseif refill > 0 then
      retry = (requested - tokens) / refill
    end
    redis.call('HSET', KEYS[1], 'tokens', tokens, 'timestamp', now)
    redis.call('EXPIRE', KEYS[1], math.ceil(math.max(60, capacity / math.max(refill, 0.001) * 2)))
    return {allowed, math.floor(tokens), retry}
    """

    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
        redis_url: str | None = None,
        fail_open: bool | None = None,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.capacity = float(limit)
        self.refill_per_second = self.capacity / window_seconds
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.fail_open = (
            fail_open
            if fail_open is not None
            else os.getenv("APP_ENV", "development").lower() not in {"prod", "production"}
        )
        self._redis: Any = (
            Redis.from_url(self.redis_url, decode_responses=False)
            if Redis and self.redis_url
            else None
        )
        self._fallback: dict[str, deque[float]] = defaultdict(deque)
        self._fallback_lock = asyncio.Lock()
        self.using_fallback = self._redis is None

    def check(self, tenant_id: str) -> None:
        """Retain the synchronous local contract used by existing unit tests."""
        now = time.monotonic()
        events = self._fallback[tenant_id]
        cutoff = now - self.window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= self.limit:
            raise RuntimeError("rate limit exceeded")
        events.append(now)

    async def acquire(self, tenant_id: str, cost: int = 1) -> RateLimitDecision:
        """Atomically consume tokens for a tenant or use the local fallback."""
        if cost < 1 or cost > self.capacity:
            raise ValueError("cost must be between one and bucket capacity")
        if self._redis is not None:
            try:
                result = await self._redis.eval(
                    self._SCRIPT,
                    1,
                    f"optimax:rate:{tenant_id}",
                    time.time(),
                    self.refill_per_second,
                    self.capacity,
                    cost,
                )
                self.using_fallback = False
                allowed, remaining, retry_after = (float(value) for value in result)
                return RateLimitDecision(bool(allowed), int(remaining), retry_after)
            except Exception:
                if not self.fail_open:
                    raise
        self.using_fallback = True
        return await self._acquire_fallback(tenant_id, cost)

    async def _acquire_fallback(self, tenant_id: str, cost: int) -> RateLimitDecision:
        """Apply equivalent token accounting under one-process test conditions."""
        now = time.monotonic()
        async with self._fallback_lock:
            events = self._fallback[tenant_id]
            cutoff = now - self.window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) + cost <= self.limit:
                for _ in range(cost):
                    events.append(now)
                return RateLimitDecision(True, self.limit - len(events), 0.0)
            retry_after = max(0.0, events[0] + self.window_seconds - now)
            return RateLimitDecision(False, 0, retry_after)


limiter = TenantRateLimiter(
    limit=int(os.getenv("RATE_LIMIT_CAPACITY", "60")),
    window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
)


async def rate_limit_request(tenant_id: str) -> RateLimitDecision:
    """Consume one tenant request token and return its decision."""
    return await limiter.acquire(tenant_id)
