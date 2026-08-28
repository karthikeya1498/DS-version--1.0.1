# WebSocket Soak-Test Runbook

**Author: Karthikeya**

## Purpose

The soak runner monitors authenticated WebSocket connection stability, traffic-event delivery, publisher failures, and API process resident memory. It writes checkpoint JSON so an interrupted run retains the last completed observation.

## Recommended 24-hour command

Start the API and Redis using the production-equivalent deployment configuration, record the API process ID, and run:

```bash
python benchmarks/soak_test_websocket.py \
  --base-url http://127.0.0.1:8000 \
  --duration-hours 24 \
  --checkpoint-seconds 300 \
  --subscribers 10 \
  --publish-interval 5 \
  --pid <api-process-id> \
  --output artifacts/websocket-soak-24h.json
```

The default sandbox is not a durable host for a 24-hour process. Run this command on a continuously available deployment or persistent machine. The weekly workflow runs a 60-second smoke version to validate that the harness, Redis service, API startup, and checkpoint writer remain operational.

## Acceptance criteria

A stable run should have zero unexplained connection errors, zero publisher errors, monotonically increasing received-event and published-batch counts, and no sustained upward RSS trend after warm-up. A reconnect caused by a controlled deployment restart should be recorded and explained separately from unexpected disconnects.

The checkpoint file is the primary handoff artifact. Preserve it with the deployment identifier, application commit SHA, Redis version, subscriber count, and publish interval when attaching it to a release or incident review.
