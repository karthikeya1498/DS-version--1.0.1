"""Fail CI when forecast metrics regress beyond the approved threshold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--baseline", type=Path, default=Path("configs/quality/model_regression_baseline.json")
    )
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate_metrics = candidate.get("metrics", candidate)
    baseline_metrics = baseline["metrics"]
    threshold = float(baseline.get("max_relative_degradation", 0.05))
    failures = []
    rows = []
    for metric in ("mae", "rmse", "smape"):
        actual = float(candidate_metrics[metric])
        reference = float(baseline_metrics[metric])
        allowed = reference * (1.0 + threshold)
        passed = actual <= allowed
        rows.append(
            {
                "metric": metric,
                "candidate": actual,
                "baseline": reference,
                "allowed_max": allowed,
                "relative_change": actual / reference - 1.0,
                "passed": passed,
            }
        )
        if not passed:
            failures.append(f"{metric}: {actual:.6f} > allowed {allowed:.6f}")
    print(
        json.dumps(
            {
                "candidate": str(args.candidate),
                "baseline": str(args.baseline),
                "threshold": threshold,
                "metrics": rows,
            },
            indent=2,
        )
    )
    if failures:
        raise SystemExit("Model regression detected: " + "; ".join(failures))


if __name__ == "__main__":
    main()
