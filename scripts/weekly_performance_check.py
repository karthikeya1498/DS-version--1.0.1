"""Run the weekly batch performance regression gate.

Author: Karthikeya
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_benchmark(updates: int, repetitions: int) -> dict[str, float | int]:
    """Execute the existing benchmark and parse its JSON result."""
    result = subprocess.run(
        [sys.executable, "benchmarks/benchmark_batch_traffic.py", "--updates", str(updates), "--repetitions", str(repetitions)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> None:
    """Evaluate the benchmark against explicit weekly regression thresholds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--updates", type=int, default=50)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--max-batch-ms", type=float, default=100.0)
    parser.add_argument("--min-reduction-percent", type=float, default=80.0)
    parser.add_argument("--output", default="artifacts/weekly-performance.json")
    args = parser.parse_args()
    if not 1 <= args.updates <= 60 or args.repetitions < 1:
        raise SystemExit("updates must be 1..60 and repetitions must be positive")
    metrics = run_benchmark(args.updates, args.repetitions)
    checks = {
        "batch_latency_within_limit": metrics["batch_mean_ms"] <= args.max_batch_ms,
        "latency_reduction_above_floor": metrics["latency_reduction_percent"] >= args.min_reduction_percent,
    }
    report = {"config": vars(args), "metrics": metrics, "checks": checks, "passed": all(checks.values())}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit("weekly performance regression gate failed")


if __name__ == "__main__":
    main()
