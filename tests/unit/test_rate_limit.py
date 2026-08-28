"""Unit tests for token-bucket decisions.

Author: Karthikeya
"""

import asyncio

from src.security.rate_limit import TenantRateLimiter


def test_token_bucket_depletes_and_isolates_tenants():
    """A tenant exhausts its bucket while another tenant remains independent."""
    limiter = TenantRateLimiter(limit=2, window_seconds=60)
    first = asyncio.run(limiter.acquire("tenant-a"))
    second = asyncio.run(limiter.acquire("tenant-a"))
    blocked = asyncio.run(limiter.acquire("tenant-a"))
    other = asyncio.run(limiter.acquire("tenant-b"))

    assert first.allowed and second.allowed
    assert not blocked.allowed
    assert blocked.remaining == 0
    assert other.allowed


def test_token_bucket_supports_batch_costs():
    """A batch cost consumes several tokens atomically in the fallback."""
    limiter = TenantRateLimiter(limit=5, window_seconds=60)
    decision = asyncio.run(limiter.acquire("batch-tenant", cost=4))
    remaining = asyncio.run(limiter.acquire("batch-tenant"))
    blocked = asyncio.run(limiter.acquire("batch-tenant"))

    assert decision.allowed and decision.remaining == 1
    assert remaining.allowed
    assert not blocked.allowed
