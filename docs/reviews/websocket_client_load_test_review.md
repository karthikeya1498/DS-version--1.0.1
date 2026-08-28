# Code Review: TypeScript WebSocket Client and Traffic Load Test

**Author: Karthikeya**  
**Review scope:** `frontend/src/main.ts`, `frontend/src/style.css`, `api/routes/realtime.py`, `src/realtime/traffic_stream.py`, and `benchmarks/load_test_websocket.py`.

## Review summary

The TypeScript client follows a clear lifecycle: request a development JWT, open the authenticated WebSocket, mark the connection live, parse typed traffic events, render route re-optimization updates, and reconnect after close or connection setup failure. The client does not retry in a tight loop; it waits three seconds between attempts and clears the pending timer when the page unloads.

The server sends a `connected` event first, emits `heartbeat` messages when no traffic update arrives for 25 seconds, and forwards `route_reoptimization` payloads from the in-process traffic stream. The integration test verifies authentication and event delivery. The load harness opens concurrent subscribers and publishes through the real authenticated REST endpoint so fan-out is measured end to end rather than by directly calling an internal queue.

## State-machine review

| State | Trigger | Client behavior |
|---|---|---|
| Connecting | Initial page load or retry timer | Fetch JWT and construct `WebSocket` with an encoded token query parameter |
| Live | WebSocket `open` event | Mark the status pill live and accept traffic messages |
| Live / event | `route_reoptimization` message | Validate the expected shape and prepend a bounded event row |
| Unavailable | Token request or socket error | Show a degraded state without breaking the seeded simulation view |
| Reconnecting | WebSocket `close` event | Schedule one retry after three seconds |
| Stopped | Browser unload | Clear the pending reconnect timer |

## Load-test protocol

The default run uses **50 subscribers and 50 concurrent traffic events**. This produces 2,500 expected subscriber-event deliveries while staying below the service’s default 60-request-per-tenant sliding-window limit. The test reports opened connections, delivery completeness, elapsed time, throughput, connection errors, and publisher errors. A run that drops any expected delivery exits nonzero.

The initial exploratory 50-subscriber/100-event run intentionally exposed the existing tenant rate limit: publisher requests beyond the first 60 were rejected with HTTP 429, and the harness was stopped rather than reporting a misleading fan-out result. The validated run uses the documented 50-event profile.

## Findings and follow-up

The current traffic stream is an in-process broadcast stream. It is appropriate for a single-process development or demonstration deployment, but a multi-replica production deployment would require a shared broker such as Redis or PostgreSQL LISTEN/NOTIFY. Tenant filtering should also be enforced at the stream subscription boundary before production multi-tenant use; the current test keeps a single tenant to measure delivery semantics without conflating isolation with throughput.

The load result was **2,500/2,500 deliveries**, with **50/50 connections opened**, **zero connection errors**, **zero publisher errors**, and **19,301.37 deliveries per second** in the local loopback environment. This is a development benchmark, not a production capacity guarantee; network distance, TLS, proxying, worker count, message size, and broker behavior must be included in a deployment benchmark.

## Review decision

**Approved with follow-up:** the client implementation is suitable for the current single-process Phase 6 demonstration. Before production deployment, add a shared event broker, server-side tenant filtering, configurable API origin, and a staged load profile that exercises rate-limit behavior separately from WebSocket fan-out.
