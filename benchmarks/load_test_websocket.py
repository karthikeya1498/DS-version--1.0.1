"""Measure authenticated WebSocket fan-out under concurrent traffic updates.

Author: Karthikeya

The harness starts no server itself. Point it at a running FastAPI instance,
then it creates concurrent subscribers and publishes traffic events through the
same authenticated REST route used by the dashboard. The measured delivery
count is subscribers multiplied by published events, which makes dropped
messages visible without requiring application-specific assumptions.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
import websockets


@dataclass(frozen=True)
class LoadTestResult:
    """Serializable summary of one WebSocket load-test run."""

    subscribers: int
    events: int
    expected_deliveries: int
    received_deliveries: int
    connections_opened: int
    elapsed_seconds: float
    deliveries_per_second: float
    connection_errors: int
    delivery_errors: int


async def get_token(client: httpx.AsyncClient, base_url: str, tenant: str) -> str:
    """Obtain the same development JWT contract used by the browser client."""
    response = await client.post(
        f"{base_url}/api/v1/auth/token",
        json={"username": "load-test", "password": "development", "tenant_id": tenant},
    )
    response.raise_for_status()
    return response.json()["access_token"]


async def subscriber(
    ws_url: str, token: str, expected_events: int, barrier: asyncio.Barrier
) -> tuple[int, int]:
    """Connect one subscriber, acknowledge readiness, and count event deliveries."""
    received = 0
    errors = 0
    try:
        async with websockets.connect(f"{ws_url}?token={token}", open_timeout=10) as socket:
            connected = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
            if connected.get("event_type") != "connected":
                raise RuntimeError("subscriber did not receive a connected event")
            await barrier.wait()
            while received < expected_events:
                event = json.loads(await asyncio.wait_for(socket.recv(), timeout=30))
                if event.get("event_type") == "route_reoptimization":
                    received += 1
    except Exception:
        errors += 1
    return received, errors


async def publish_events(
    client: httpx.AsyncClient, base_url: str, token: str, event_count: int
) -> int:
    """Publish traffic changes concurrently and return failed HTTP request count."""
    async def publish(index: int) -> bool:
        response = await client.post(
            f"{base_url}/api/v1/traffic/updates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "zone_id": f"load-zone-{index % 8}",
                "multiplier": 1.0 + ((index % 5) * 0.1),
                "affected_vehicle_ids": [f"vehicle-{index % 16}"],
            },
        )
        return response.is_success

    results = await asyncio.gather(*(publish(index) for index in range(event_count)))
    return sum(not success for success in results)


async def run_load_test(args: argparse.Namespace) -> LoadTestResult:
    """Run the subscriber and publisher phases with a shared monotonic clock."""
    base_url = args.base_url.rstrip("/")
    ws_url = base_url.replace("https://", "wss://").replace("http://", "ws://") + "/api/v1/ws/traffic"
    async with httpx.AsyncClient(timeout=30) as client:
        token = await get_token(client, base_url, args.tenant)
        barrier = asyncio.Barrier(args.subscribers + 1)
        subscriber_tasks = [
            asyncio.create_task(subscriber(ws_url, token, args.events, barrier))
            for _ in range(args.subscribers)
        ]
        started = time.perf_counter()
        await barrier.wait()
        publish_errors = await publish_events(client, base_url, token, args.events)
        outcomes = await asyncio.gather(*subscriber_tasks)
        elapsed = time.perf_counter() - started

    received = sum(item[0] for item in outcomes)
    connection_errors = sum(item[1] for item in outcomes)
    expected = args.subscribers * args.events
    return LoadTestResult(
        subscribers=args.subscribers,
        events=args.events,
        expected_deliveries=expected,
        received_deliveries=received,
        connections_opened=args.subscribers - connection_errors,
        elapsed_seconds=round(elapsed, 4),
        deliveries_per_second=round(received / elapsed if elapsed else 0.0, 2),
        connection_errors=connection_errors,
        delivery_errors=publish_errors,
    )


def parse_args() -> argparse.Namespace:
    """Parse conservative defaults that are safe for local development."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--tenant", default="load-test")
    parser.add_argument("--subscribers", type=int, default=50)
    parser.add_argument("--events", type=int, default=50, help="events per run; keep below the default 60-request tenant limit")
    parser.add_argument("--output", type=str)
    return parser.parse_args()


def write_result(path: str, payload: dict[str, Any]) -> None:
    """Persist a completed result outside the asynchronous request path."""
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


async def main() -> None:
    """Execute the run and fail clearly when delivery is incomplete."""
    args = parse_args()
    if args.subscribers < 1 or args.events < 1:
        raise SystemExit("--subscribers and --events must be positive")
    result = await run_load_test(args)
    payload: dict[str, Any] = asdict(result)
    print(json.dumps(payload, indent=2))
    if args.output:
        write_result(args.output, payload)
    if result.connection_errors or result.delivery_errors or result.received_deliveries != result.expected_deliveries:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
