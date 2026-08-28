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


## Browser verification findings

The first browser check exposed a deployment configuration defect: the Vite development server rejected the temporary proxied host, and the API origin was hardcoded to localhost. The optimization branch now includes Vite `allowedHosts` configuration, typed `VITE_API_ORIGIN` support, and configurable API CORS origins. After restarting the API and dashboard with the exposed origins, the browser displayed **Live** for the WebSocket connection.

A live traffic update for zone `live-verification` with a `1.35` multiplier and `vehicle-qa` was published through the API and appeared in the dashboard event list. The seeded scenario action also completed successfully with 6 total orders, 6 delivered orders, 0 late deliveries, 0 unserved orders, and a total cost of 1.413. This confirms the REST simulation path and live WebSocket telemetry operate concurrently in the deployed-equivalent environment.
