# Batch and Database Performance Optimization Report

**Author: Karthikeya**

## Scope

This pull request optimizes the merged traffic-update path without changing the public API contract. The traffic stream now snapshots subscribers and uses bounded `put_nowait` writes, avoiding one coroutine yield per subscriber for every event. A slow subscriber still loses the oldest queued event when its 100-event queue is full, while the latest event is retained.

The PostgreSQL schema now includes indexes for common operational access patterns: pending orders by status and time window, traffic history by zone and descending observation time, decisions by scenario and creation time, and traces by decision and creation time. These are additive `CREATE INDEX IF NOT EXISTS` statements and preserve existing keys and constraints.

## Local latency evidence

The 50-update comparison was repeated five times after the fan-out optimization under the Redis-backed middleware.

| Metric | Individual requests | Batch request |
|---|---:|---:|
| HTTP requests | 50 | 1 |
| Mean latency | 144.138 ms | 3.060 ms |
| Latency reduction | — | 97.88% |
| Request reduction | — | 50× |

The result is a local TestClient/Redis measurement. It demonstrates request-amortization behavior, not a production capacity guarantee.

## Post-deployment stability verification

The repository does not contain a publicly reachable production dashboard URL; its deployment documentation exposes local API and Streamlit addresses. Therefore, the post-deployment check uses the deployed-equivalent FastAPI process and browser dashboard build locally, with the same authentication and WebSocket contracts. The verification should confirm API health, TypeScript production build, authenticated WebSocket connection, receipt of traffic events, reconnect behavior after a server restart, and no loss of the REST simulation path.

A real external deployment URL can be substituted with `BASE_URL` and `WS_URL` when the hosting target is available.
