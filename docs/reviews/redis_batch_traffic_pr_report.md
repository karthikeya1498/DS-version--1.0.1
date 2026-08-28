# Redis Token Bucket and Batch Traffic Update Report

**Author: Karthikeya**

## Implementation

The server now uses `TenantRateLimiter` in `src/security/rate_limit.py`. When `REDIS_URL` is configured, each tenant bucket is stored under `optimax:rate:<tenant>` in Redis. A Lua script updates token count, refill timestamp, expiry, and allow/deny state atomically, which prevents races across API workers and replicas. The default policy remains 60 tokens per 60 seconds per tenant, equivalent to one replenished token per second with a burst capacity of 60.

When Redis is unavailable or not configured, the module uses a bounded in-process fallback for deterministic local tests. Production-like deployments should configure Redis and monitor fallback activation. The middleware now awaits the limiter and returns `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining` headers when it returns HTTP 429.

Docker Compose now includes a health-checked Redis 7 service and passes `REDIS_URL=redis://redis:6379/0` to the API container. Redis and token-bucket settings are included in `.env.example`.

## Batch endpoint

`POST /api/v1/traffic/updates/batch` accepts one to 100 validated `TrafficUpdate` objects. It authenticates through the existing tenant JWT dependency, consumes one HTTP request token, and publishes the individual route-reoptimization events concurrently with `asyncio.gather`. The original single-update endpoint remains backward compatible.

## Integration coverage

The tests verify successful authenticated batch fan-out, exact event count and zone identity, empty and oversized payload rejection, token-bucket depletion, tenant isolation, and the Redis-backed middleware path using a local Redis database. The full Python suite passed **43 tests**; the Redis-backed realtime and batch integration subset passed **6 tests**.

## Latency comparison

The benchmark compares 50 individual authenticated requests with one authenticated batch request containing the same 50 updates, repeated five times under the Redis-backed middleware.

| Metric | Individual requests | One batch request |
|---|---:|---:|
| HTTP requests per trial | 50 | 1 |
| Mean latency | 188.918 ms | 3.316 ms |
| Request reduction | — | 50× fewer requests |
| Mean latency reduction | — | **98.24%** |

This is a local TestClient/Redis measurement, not a production capacity guarantee. Network latency, TLS, proxying, event-broker behavior, payload size, and downstream route processing should be included in deployment benchmarks.

## Pull request review scope

The changes should be reviewed as separate topics: limiter implementation, middleware headers, batch API contract, Redis Compose wiring, and tests/benchmark evidence. Follow-up production work includes Redis authentication/TLS configuration, metrics for fallback activation and rejected requests, server-side tenant filtering before WebSocket queue insertion, and a dedicated traffic-ingest quota distinct from general API traffic.
