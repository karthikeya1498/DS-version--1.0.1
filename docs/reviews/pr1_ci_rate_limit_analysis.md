# Pull Request #1 CI/CD and Rate-Limit Analysis

**Author: Karthikeya**  
**Pull request:** [#1](https://github.com/karthikeya1498/DS-version--1.0.1/pull/1)  
**Reviewed head:** `6d6674e`

## CI/CD result

Pull request #1 is open and currently reports a clean merge state. GitHub reports all five checks successful: the Docker build, Python tests on push, Python tests on pull request, Java JUnit on push, and Java JUnit on pull request.

| Check | Result | Interpretation |
|---|---:|---|
| `build/docker` | Success | The repository Docker image builds successfully |
| `tests/test` on push | Success | The pushed branch passed the Python suite |
| `tests/test` on pull request | Success | The pull-request merge commit passed the Python suite |
| `java-dsa/junit` on push | Success | Java DSA tests pass on the branch push |
| `java-dsa/junit` on pull request | Success | Java DSA tests pass in PR context |

The automated feedback contains runner-maintenance warnings rather than application failures. GitHub reports that `actions/checkout@v4` and `actions/setup-java@v4` target Node.js 20 and are being forced onto Node.js 24 by the runner. The `setup-java` annotation also states that v4 is deprecated and recommends v5. These warnings do not invalidate the build, but the workflows should be migrated to current action versions in a maintenance PR.

## 100-event stress-test root cause

The server uses a process-local sliding-window limiter:

```python
class TenantRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit, self.window_seconds = limit, window_seconds
```

The HTTP middleware decodes the bearer token, extracts `tenant_id`, and applies `limiter.check(tenant)` to every non-public HTTP request. The traffic publisher endpoint is therefore limited by **60 requests per 60 seconds per tenant**. The token endpoint is public, but `/api/v1/traffic/updates` is not.

The 100-event run used one tenant and issued 100 concurrent POST requests. The first 60 requests were accepted into the sliding window; the remaining requests were rejected with HTTP 429. This is expected behavior from the current policy, not a WebSocket fan-out failure. The WebSocket connection itself is not handled by the HTTP middleware and has no equivalent connection or message quota. The stress profile therefore tested two controls at once: REST event-ingest throttling and WebSocket delivery.

The validated 50-event run stayed below the 60-request window and achieved 2,500/2,500 subscriber deliveries across 50 subscribers, with zero connection or publisher errors. That result supports the conclusion that the observed 100-event failure was caused by the REST rate limit rather than the WebSocket stream.

## Adjustment options

| Option | Benefit | Cost / risk | Recommendation |
|---|---|---|---|
| Raise the per-tenant limit to 120–600/minute | Simple and preserves the current API | Still process-local; may permit bursts that overload downstream routing | Suitable for development and controlled internal tenants |
| Add a dedicated traffic-ingest quota | Separates high-rate telemetry from ordinary API calls | Requires endpoint classification and configuration | Recommended immediate server-side adjustment |
| Add batching, e.g. 20 updates/request | Reduces HTTP overhead and limiter consumption | Requires client and schema changes; larger failure units | Recommended for production traffic producers |
| Use a token bucket with burst capacity and refill rate | Models bursts more naturally than a fixed sliding window | More implementation and tuning complexity | Recommended after measuring real traffic |
| Move limiter state to Redis or another shared store | Correct across multiple workers/replicas | Adds infrastructure and operational dependency | Required for multi-replica production |
| Return `Retry-After` and rate-limit headers | Makes client backoff deterministic and debuggable | Small API contract addition | Recommended regardless of chosen quota |

## Proposed staged policy

For the current single-process development service, keep the default **60 requests/minute** for general authenticated API calls, but assign `/api/v1/traffic/updates` a dedicated configurable quota such as **600 requests/minute per tenant**, with a conservative burst cap. This avoids weakening protection on every API route merely to accommodate traffic telemetry.

For the dashboard and load harness, handle HTTP 429 explicitly: read `Retry-After`, pause publishing, and retry only within a bounded deadline. The load test should report accepted events, rejected events, and delivered events separately rather than treating all 100 requested events as expected deliveries when the server intentionally rejects some.

For production, replace the process-local deque with a shared Redis-backed token bucket. Include tenant ID, route class, and optionally authenticated client identity in the key. Add `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` headers to rejected HTTP responses. Add a separate WebSocket connection limit and per-connection message-rate guard, and enforce tenant filtering before placing events into subscriber queues.

The recommended sequence is therefore: first separate the traffic-ingest quota and improve 429 observability; second add batching and bounded client retry; third migrate shared state and tenant-aware WebSocket filtering before horizontal scaling.

## Review conclusion

Pull request #1 is healthy from a CI/CD correctness perspective. The only automated feedback requiring maintenance is the GitHub Action runtime deprecation warning. The 100-event stress-test result is an intentional rate-limit response: the endpoint currently accepts 60 requests per tenant per 60-second window, while the test attempted 100 requests concurrently. No evidence indicates that the WebSocket delivery path dropped messages under the validated 50-event profile.
