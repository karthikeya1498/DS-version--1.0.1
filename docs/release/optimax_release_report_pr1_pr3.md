# OPTIMA-X Release Report: Pull Requests #1–#3

**Author: Karthikeya**  
**Release scope:** Phases 1–6 connectivity, live traffic telemetry, Redis-backed rate limiting, batch ingestion, performance optimization, and deployment verification.

## Executive summary

This release consolidates the work reviewed through Pull Requests [#1](https://github.com/karthikeya1498/DS-version--1.0.1/pull/1), [#2](https://github.com/karthikeya1498/DS-version--1.0.1/pull/2), and [#3](https://github.com/karthikeya1498/DS-version--1.0.1/pull/3). Pull Request #1 established the review and load-testing process for the live WebSocket dashboard. Pull Request #2 introduced a distributed Redis token bucket and authenticated batch traffic ingestion. Pull Request #3 optimized in-process traffic fan-out, added operational PostgreSQL indexes, and corrected cross-origin deployment configuration for the browser dashboard.

Pull Requests #2 and #3 were merged into `main`; Pull Request #1 remains open as the original WebSocket review and load-test record. The resulting main branch contains the Python orchestration and API layer, Java DSA module, SQL persistence schema, TypeScript/HTML/CSS operations dashboard, Redis-backed rate limiting, batch traffic ingestion, integration tests, and CI quality gates.

## Pull request ledger

| Pull request | Scope | Key implementation | Final status |
|---|---|---|---|
| #1 | WebSocket review and load testing | Typed dashboard WebSocket client review, reconnect analysis, concurrent traffic load harness, and review artifacts | Open review artifact |
| #2 | Distributed throttling and batch ingestion | Atomic Redis Lua token bucket, local fallback, rate-limit headers, batch traffic endpoint, Redis Compose service, and edge-case tests | Merged as `6514dfc` |
| #3 | Batch and database performance | Non-blocking stream fan-out, PostgreSQL operational indexes, configurable CORS/API origin, and dashboard stability evidence | Merged as `0448e3f` |

## Functional changes

### Live WebSocket telemetry

The TypeScript dashboard obtains a short-lived development JWT, opens the authenticated `/api/v1/ws/traffic` connection, renders `route_reoptimization` events, bounds the visible event list to eight rows, and reports connection states including Connecting, Live, Unavailable, and Reconnecting. The reconnect timer is cleared during page unload, and the existing seeded simulation path remains independent from telemetry availability.

### Redis-backed rate limiting

The API now uses an atomic Redis Lua token bucket keyed by tenant. The implementation is configurable through `REDIS_URL`, `RATE_LIMIT_CAPACITY`, and `RATE_LIMIT_WINDOW_SECONDS`, while a deterministic local fallback supports tests and Redis-free development. Throttled responses expose `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining` headers. Docker Compose provides Redis 7 with a health check.

### Batch traffic ingestion

`POST /api/v1/traffic/updates/batch` accepts one to 100 validated traffic updates and publishes the resulting route-reoptimization events under one authenticated HTTP request. The original single-update endpoint remains available for backward compatibility. Batch requests consume one HTTP rate-limit token, preventing the 100-event stress scenario from being incorrectly interpreted as WebSocket delivery loss.

### Processing and database performance

Traffic fan-out now snapshots subscribers and uses bounded non-blocking queue writes. A full subscriber queue drops its oldest event and retains the newest event, preventing a slow client from blocking publishers. The SQL schema adds indexes for pending orders by status and window, traffic history by zone and observation time, decisions by scenario and creation time, and decision traces by decision and creation time.

### Deployment configuration

The dashboard API origin is configurable through `VITE_API_ORIGIN`, with localhost retained as the development default. FastAPI CORS origins are configurable through `CORS_ALLOWED_ORIGINS`. Vite explicitly permits the managed proxied host used for verification while retaining host validation.

## Validation evidence

| Validation | Result |
|---|---:|
| Python unit and integration suite before merge | 45 passed |
| Redis-backed batch and realtime integration tests | Passed |
| Java Maven/JUnit suite | Passed |
| TypeScript compiler and Vite build | Passed |
| Docker build workflow | Passed |
| Main-branch post-merge workflows | `java-dsa`, `tests`, and `build` all successful |
| 50-subscriber / 50-event WebSocket load test | 2,500 of 2,500 deliveries |
| Live dashboard event verification | Passed |
| Live dashboard seeded scenario | 6 of 6 orders delivered; cost 1.413 |

The earlier 50-update benchmark measured 97.88% lower mean latency for a single batch request than 50 individual requests. The later three-repetition check measured 2.907 ms batch latency, 173.895 ms individual latency, and 98.33% reduction. These are local reproducibility measurements, not production capacity guarantees.

## CI/CD and operational notes

The repository runs Python tests, Java DSA tests, and Docker build verification on pushes and pull requests. The new weekly workflow runs the performance gate, a 60-second WebSocket soak smoke test, and an optional external deployment health check when the repository variable `DEPLOYMENT_BASE_URL` is configured.

The soak runner supports a 24-hour default duration, configurable subscriber count and publish interval, process RSS sampling from Linux procfs, and checkpoint JSON output. A 30-second local smoke run with five subscribers produced five opened connections, zero connection errors, zero publisher errors, 145 received events, and stable RSS at approximately 80.4 MB across the final checkpoints. A full 24-hour run was not claimed in this release because the interactive sandbox cannot guarantee continuous execution for an entire day; the workflow is ready to run it on a persistent deployment environment.

The GitHub Actions runner continues to emit a non-blocking maintenance warning that some existing actions target Node.js 20 while the runner forces Node.js 24. This should be addressed in a future maintenance PR by upgrading the affected actions where supported.

## Release decision

The release is suitable for continued development and staging-style operational validation. The primary remaining production tasks are to configure `DEPLOYMENT_BASE_URL`, run the full 24-hour soak in a persistent environment, add external metrics export for memory and connection time series, and upgrade workflow actions affected by the Node.js runtime warning.

## References

[1]: https://github.com/karthikeya1498/DS-version--1.0.1/pull/1 "OPTIMA-X Pull Request #1"

[2]: https://github.com/karthikeya1498/DS-version--1.0.1/pull/2 "OPTIMA-X Pull Request #2"

[3]: https://github.com/karthikeya1498/DS-version--1.0.1/pull/3 "OPTIMA-X Pull Request #3"
