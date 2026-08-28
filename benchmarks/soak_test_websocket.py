"""Long-duration WebSocket soak test with checkpointed stability metrics.

Author: Karthikeya
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
import websockets


def rss_bytes(pid: int | None) -> int | None:
    """Read resident memory from Linux procfs when a server PID is supplied."""
    if pid is None:
        return None
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except (FileNotFoundError, ValueError):
        return None
    return None


async def get_token(base_url: str, tenant: str) -> str:
    """Request a short-lived development JWT for the soak tenant."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/v1/auth/token",
            json={"username": "soak", "password": "development", "tenant_id": tenant},
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def subscriber(base_url: str, tenant: str, stop: asyncio.Event, metrics: dict[str, int]) -> None:
    """Maintain one WebSocket connection and count received traffic events."""
    ws_url = base_url.replace("http", "ws", 1) + "/api/v1/ws/traffic"
    while not stop.is_set():
        try:
            jwt = await get_token(base_url, tenant)
            async with websockets.connect(f"{ws_url}?token={jwt}", ping_interval=20) as socket:
                metrics["connections_opened"] += 1
                await socket.recv()
                while not stop.is_set():
                    event = await asyncio.wait_for(socket.recv(), timeout=30)
                    if json.loads(event).get("event_type") == "route_reoptimization":
                        metrics["events_received"] += 1
        except (OSError, TimeoutError, websockets.WebSocketException, httpx.HTTPError):
            metrics["connection_errors"] += 1
            await asyncio.sleep(1)


async def publish_loop(base_url: str, tenant: str, interval: float, stop: asyncio.Event, metrics: dict[str, int]) -> None:
    """Publish deterministic traffic updates until the soak interval ends."""
    index = 0
    while not stop.is_set():
        try:
            jwt = await get_token(base_url, tenant)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/api/v1/traffic/updates/batch",
                    headers={"Authorization": f"Bearer {jwt}"},
                    json={"updates": [{"zone_id": f"soak-{index}", "multiplier": 1.15}]},
                )
                response.raise_for_status()
                metrics["batches_published"] += 1
        except (OSError, httpx.HTTPError):
            metrics["publisher_errors"] += 1
        index += 1
        await asyncio.sleep(interval)


async def run(args: argparse.Namespace) -> dict[str, object]:
    """Run the soak workload and persist checkpoint snapshots."""
    started = time.time()
    deadline = started + args.duration_seconds
    stop = asyncio.Event()
    metrics = {"connections_opened": 0, "connection_errors": 0, "events_received": 0, "batches_published": 0, "publisher_errors": 0}
    subscribers = [asyncio.create_task(subscriber(args.base_url, args.tenant, stop, metrics)) for _ in range(args.subscribers)]
    publisher = asyncio.create_task(publish_loop(args.base_url, args.tenant, args.publish_interval, stop, metrics))
    checkpoints: list[dict[str, object]] = []
    try:
        while time.time() < deadline:
            await asyncio.sleep(min(args.checkpoint_seconds, max(0, deadline - time.time())))
            checkpoint = {"timestamp": datetime.now(UTC).isoformat(), "elapsed_seconds": round(time.time() - started, 2), "rss_bytes": rss_bytes(args.pid), **metrics}
            checkpoints.append(checkpoint)
            Path(args.output).write_text(json.dumps({"config": vars(args), "checkpoints": checkpoints, "final": checkpoint}, indent=2))
    finally:
        stop.set()
        await asyncio.gather(publisher, *subscribers, return_exceptions=True)
    return {"config": vars(args), "checkpoints": checkpoints, "final": checkpoints[-1] if checkpoints else metrics}


def main() -> None:
    """Parse options and execute the checkpointed soak test."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--duration-hours", type=float, default=24.0)
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--checkpoint-seconds", type=float, default=300.0)
    parser.add_argument("--subscribers", type=int, default=10)
    parser.add_argument("--publish-interval", type=float, default=5.0)
    parser.add_argument("--tenant", default="soak-test")
    parser.add_argument("--pid", type=int)
    parser.add_argument("--output", default="artifacts/websocket-soak.json")
    args = parser.parse_args()
    if args.duration_seconds is None:
        args.duration_seconds = args.duration_hours * 3600
    if args.duration_seconds <= 0 or args.subscribers <= 0 or args.checkpoint_seconds <= 0:
        raise SystemExit("duration, subscribers, and checkpoint interval must be positive")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps(asyncio.run(run(args)), indent=2))


if __name__ == "__main__":
    main()
