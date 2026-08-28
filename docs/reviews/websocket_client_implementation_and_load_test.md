# OPTIMA-X WebSocket Client Implementation and Load-Test Report

**Author: Karthikeya**  
**Repository:** `karthikeya1498/DS-version--1.0.1`  
**Pull request:** [#1](https://github.com/karthikeya1498/DS-version--1.0.1/pull/1)

## TypeScript client implementation

The browser client is implemented in `frontend/src/main.ts`. It keeps the REST simulation path and the live traffic path separate but visible in one operations dashboard. The client uses typed contracts for `SimulationMetrics`, `SimulationResponse`, `TrafficEvent`, and `TokenResponse`.

The connection flow is:

```text
page load
  -> POST /api/v1/auth/token
  -> receive short-lived development JWT
  -> open /api/v1/ws/traffic?token=<encoded-token>
  -> receive connected event
  -> mark dashboard Live
  -> parse route_reoptimization events
  -> render bounded event list
```

The token request uses the same API contract as the integration test:

```typescript
const response = await fetch(TOKEN_URL, {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({
    username: 'dashboard',
    password: 'development',
    tenant_id: 'dashboard',
  }),
});
```

The WebSocket URL is constructed from the API origin, converts `http` to `ws` and `https` to `wss`, and URL-encodes the token before adding it as a query parameter. Incoming messages are parsed as `TrafficEvent`; only `route_reoptimization` messages create visible rows. Each row contains the zone, traffic multiplier, affected vehicles, and local display time. The list is capped at eight rows to prevent unbounded DOM growth.

## Reconnection handling

The client uses the following state machine:

| State | Trigger | Behavior |
|---|---|---|
| Connecting | Initial load or retry attempt | Obtain a JWT and construct the socket |
| Live | WebSocket `open` event | Mark the connection healthy and accept messages |
| Unavailable | Token request or socket error | Show degraded state without disabling REST simulation |
| Reconnecting | WebSocket `close` event | Schedule one retry after 3 seconds |
| Stopped | `beforeunload` | Clear any pending reconnect timer |

The reconnect path is deliberately bounded by a fixed three-second delay instead of a tight loop. A socket `close` event schedules the next attempt with `window.setTimeout`; a browser unload clears that timer. In a production deployment, this can be extended with exponential backoff and jitter, but the current behavior is deterministic and easy to test.

The FastAPI server sends a `connected` event immediately after authentication, sends `heartbeat` events after 25 seconds without traffic, and forwards `route_reoptimization` events from the in-process traffic stream. The current server stream is suitable for the single-process demonstration. A multi-replica deployment needs a shared broker and subscription-time tenant filtering.

## Load-test harness

`benchmarks/load_test_websocket.py` is a reusable asyncio harness. It obtains a JWT, opens concurrent WebSocket subscribers, waits until all subscribers are ready using an `asyncio.Barrier`, and then publishes traffic updates concurrently through `POST /api/v1/traffic/updates`. Each subscriber counts only `route_reoptimization` events. The harness fails if any expected delivery, connection, or publisher request is missing.

Run it against a local API with:

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
python3 benchmarks/load_test_websocket.py \
  --base-url http://127.0.0.1:8000 \
  --subscribers 50 \
  --events 50 \
  --output /tmp/optimax-ws-load.json
```

The initial exploratory profile of 50 subscribers and 100 events exposed the configured 60-request-per-tenant REST rate limit: requests beyond the limit returned HTTP 429. That run was stopped rather than reported as a false fan-out result. The validated profile uses 50 events and measures WebSocket delivery without crossing that default throttle.

## Verified local result

| Metric | Result |
|---|---:|
| Concurrent subscribers | 50 |
| Published traffic events | 50 |
| Expected deliveries | 2,500 |
| Received deliveries | 2,500 |
| Connections opened | 50 |
| Connection errors | 0 |
| Publisher errors | 0 |
| Elapsed loopback time | 0.1295 seconds |
| Delivery throughput | 19,301.37 deliveries/second |

This is a local loopback development measurement, not a production capacity guarantee. A production benchmark should include TLS, network latency, reverse proxy behavior, multiple worker processes, realistic message sizes, broker fan-out, and tenant isolation.

## Validation and review activity

The complete repository validation passed: Python compilation, Ruff, **39 Python tests**, Java Maven/JUnit tests, TypeScript checking, Vite production build, and the explicit end-to-end smoke test. The smoke test returned HTTP 200 for health, authentication, simulation, forecasting, and routing requests.

The work is published in pull request [#1](https://github.com/karthikeya1498/DS-version--1.0.1/pull/1), which includes a structured review checklist and comment. Its Python tests, Java DSA, and Docker checks are all green, and the PR merge state is clean.
