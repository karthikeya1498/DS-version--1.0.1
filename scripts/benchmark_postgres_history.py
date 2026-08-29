"""Benchmark PostgreSQL history-query behavior under concurrent load.

Author: Karthikeya

The benchmark is intentionally opt-in and requires DATABASE_URL. It measures
p50/p95/p99 latency, throughput, errors, and representative EXPLAIN plans for
partition-pruned traffic history and DecisionRecord queries. It does not claim
production capacity; run it against a disposable PostgreSQL environment that
matches the target version and indexes.
"""
from __future__ import annotations

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from os import environ
from uuid import UUID, uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

try:
    from scripts.manage_history import ensure_traffic_partitions
except ModuleNotFoundError:  # Direct execution places the scripts directory on sys.path.
    from manage_history import ensure_traffic_partitions

TRAFFIC_QUERY = text(
    "SELECT zone_id, observed_at, multiplier FROM optima.traffic_history "
    "WHERE tenant_id = :tenant AND zone_id = :zone AND observed_at >= :start "
    "AND observed_at < :end ORDER BY observed_at DESC LIMIT 100"
)
DECISION_QUERY = text(
    "SELECT decision_id, scenario_id, algorithm, status, created_at "
    "FROM optima.decision_record WHERE tenant_id = :tenant AND scenario_id = :scenario "
    "AND created_at >= :start AND created_at < :end ORDER BY created_at DESC LIMIT 100"
)


@dataclass(frozen=True)
class QueryResult:
    name: str
    latencies_ms: list[float]
    errors: int

    @property
    def throughput(self) -> float:
        total_seconds = sum(self.latencies_ms) / 1000
        return len(self.latencies_ms) / total_seconds if total_seconds else 0.0

    def summary(self) -> dict[str, float | int | str]:
        values = sorted(self.latencies_ms)
        percentile = lambda fraction: values[min(len(values) - 1, int(len(values) * fraction))]
        return {
            "query": self.name,
            "requests": len(values),
            "errors": self.errors,
            "p50_ms": round(percentile(0.50), 3),
            "p95_ms": round(percentile(0.95), 3),
            "p99_ms": round(percentile(0.99), 3),
            "mean_ms": round(statistics.fmean(values), 3),
            "throughput_per_second": round(self.throughput, 2),
        }


def _seed(engine: Engine, rows: int) -> tuple[UUID, UUID, datetime, datetime]:
    start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=32)
    ensure_traffic_partitions(engine, start, months=2)
    with engine.begin() as connection:
        tenant = connection.execute(
            text("INSERT INTO optima.tenant (tenant_key, display_name) VALUES (:key, 'benchmark') RETURNING tenant_id"),
            {"key": f"benchmark-{uuid4().hex}"},
        ).scalar_one()
        scenario = connection.execute(
            text("INSERT INTO optima.scenario (tenant_id, scenario_key, seed, status, config, starts_at) VALUES (:tenant, :key, 42, 'created', '{}'::jsonb, :start) RETURNING scenario_id"),
            {"tenant": tenant, "key": f"benchmark-{uuid4().hex}", "start": start},
        ).scalar_one()
        traffic_rows = [
            {"tenant": tenant, "zone": f"z{i % 20}", "observed": start + timedelta(minutes=i), "multiplier": 1.0 + (i % 40) / 100}
            for i in range(rows)
        ]
        connection.execute(
            text("INSERT INTO optima.traffic_history (tenant_id, zone_id, observed_at, multiplier, source) VALUES (:tenant, :zone, :observed, :multiplier, 'benchmark')"),
            traffic_rows,
        )
        decision_rows = [
            {"tenant": tenant, "scenario": scenario, "algorithm": "benchmark", "action": '{"route": []}', "created": start + timedelta(minutes=i)}
            for i in range(max(1, rows // 5))
        ]
        connection.execute(
            text("INSERT INTO optima.decision_record (tenant_id, scenario_id, algorithm, selected_action, state_reference, created_at) VALUES (:tenant, :scenario, :algorithm, CAST(:action AS jsonb), 'benchmark', :created)"),
            decision_rows,
        )
        connection.execute(text("ANALYZE optima.traffic_history"))
        connection.execute(text("ANALYZE optima.decision_record"))
    return tenant, scenario, start, end


def _explain(engine: Engine, query, params: dict[str, object]) -> dict:
    explain = text(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query.text}")
    with engine.connect() as connection:
        return connection.execute(explain, params).scalar_one()[0]


def _run_concurrent(engine: Engine, name: str, query, params: dict[str, object], workers: int, requests: int) -> QueryResult:
    def one() -> float:
        started = time.perf_counter()
        with engine.connect() as connection:
            connection.execute(query, params).all()
        return (time.perf_counter() - started) * 1000

    latencies: list[float] = []
    errors = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(one) for _ in range(requests)]
        for future in as_completed(futures):
            try:
                latencies.append(future.result())
            except Exception:
                errors += 1
    return QueryResult(name, latencies, errors)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=5000)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--requests", type=int, default=200)
    args = parser.parse_args()
    if args.rows < 1 or args.workers < 1 or args.requests < 1:
        raise SystemExit("rows, workers, and requests must be positive")
    url = environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is required; use a disposable PostgreSQL database")
    engine = create_engine(url, pool_size=args.workers, max_overflow=args.workers, pool_pre_ping=True)
    tenant, scenario, start, end = _seed(engine, args.rows)
    params = {"tenant": tenant, "zone": "z1", "scenario": scenario, "start": start, "end": end}
    print({"dataset_rows": args.rows, "workers": args.workers, "requests_per_query": args.requests})
    print({"traffic_plan": _explain(engine, TRAFFIC_QUERY, params)})
    print({"decision_plan": _explain(engine, DECISION_QUERY, params)})
    for result in (
        _run_concurrent(engine, "traffic_history", TRAFFIC_QUERY, params, args.workers, args.requests),
        _run_concurrent(engine, "decision_record", DECISION_QUERY, params, args.workers, args.requests),
    ):
        print(result.summary())
    engine.dispose()


if __name__ == "__main__":
    main()
