"""Compare individual and batched traffic-update request latency.

Author: Karthikeya
"""

from __future__ import annotations

import argparse
import json
import time
from statistics import mean

from fastapi.testclient import TestClient

from api.main import app
from src.security.auth import create_token


def updates(count: int) -> list[dict]:
    """Create a deterministic batch payload."""
    return [
        {"zone_id": f"benchmark-zone-{i}", "multiplier": 1.1, "affected_vehicle_ids": []}
        for i in range(count)
    ]


def run(count: int, repetitions: int) -> dict[str, float | int]:
    """Measure wall-clock request time in one process with fresh tenant keys."""
    client = TestClient(app)
    individual_samples: list[float] = []
    batch_samples: list[float] = []
    for repetition in range(repetitions):
        individual_token = create_token("benchmark", f"individual-{repetition}")
        started = time.perf_counter()
        for update in updates(count):
            response = client.post(
                "/api/v1/traffic/updates",
                headers={"Authorization": f"Bearer {individual_token}"},
                json=update,
            )
            response.raise_for_status()
        individual_samples.append(time.perf_counter() - started)

        batch_token = create_token("benchmark", f"batch-{repetition}")
        started = time.perf_counter()
        response = client.post(
            "/api/v1/traffic/updates/batch",
            headers={"Authorization": f"Bearer {batch_token}"},
            json={"updates": updates(count)},
        )
        response.raise_for_status()
        batch_samples.append(time.perf_counter() - started)

    individual = mean(individual_samples)
    batch = mean(batch_samples)
    return {
        "updates_per_request": count,
        "repetitions": repetitions,
        "individual_mean_ms": round(individual * 1000, 3),
        "batch_mean_ms": round(batch * 1000, 3),
        "latency_reduction_percent": round((1 - batch / individual) * 100, 2),
        "request_reduction_factor": count,
    }


def main() -> None:
    """Run the benchmark and emit machine-readable JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--updates", type=int, default=50)
    parser.add_argument("--repetitions", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.updates <= 60 or args.repetitions < 1:
        raise SystemExit("updates must be 1..60 and repetitions must be positive")
    print(json.dumps(run(args.updates, args.repetitions), indent=2))


if __name__ == "__main__":
    main()
