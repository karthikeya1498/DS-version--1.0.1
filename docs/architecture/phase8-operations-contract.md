# Phase 8 Operations Contract

**Author: Karthikeya**

Phase 8 exposes two operator-facing endpoints. `GET /api/v1/operations/readiness` reports service readiness, PostgreSQL configuration state, the `optima` lineage schema, and all eight phase contracts. `GET /api/v1/operations/metrics` reports process-local request counts, error counts, total latency, and average latency by route.

Metrics are intentionally process-local in this first slice. They provide immediate diagnostics without claiming durable observability. The next persistence increment should write periodic snapshots to PostgreSQL `system_event` and preserve tenant-aware dimensions. A readiness response with `configured: false` means the database URL is not present; it does not claim that PostgreSQL is unhealthy.
