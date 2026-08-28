"""Production lifecycle management for OPTIMA-X historical data.

Author: Karthikeya

Examples:
    python scripts/manage_history.py ensure-partitions --months-ahead 3
    python scripts/manage_history.py archive-traffic --before 2025-01-01
    python scripts/manage_history.py archive-decisions --before 2025-01-01T00:00:00+00:00

The script is intentionally explicit: it never deletes the default traffic
partition, requires a PostgreSQL URL, uses bounded identifiers, and performs
archive/delete operations in one transaction. Run it from a scheduler with
least-privilege credentials and retain the emitted audit log.
"""

from __future__ import annotations

import argparse
import os
import re
from collections.abc import Iterable
from datetime import UTC, datetime

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

SCHEMA = "optima"
ARCHIVE_SCHEMA = "archive"
PARTITION_TABLE = "traffic_history"
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


def quote_identifier(identifier: str) -> str:
    """Quote a generated SQL identifier after strict validation."""
    if not _IDENTIFIER.fullmatch(identifier):
        raise ValueError(f"unsafe SQL identifier: {identifier!r}")
    return f'"{identifier}"'


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include an explicit timezone")
    return parsed.astimezone(UTC)


def month_start(year: int, month: int) -> datetime:
    return datetime(year, month, 1, tzinfo=UTC)


def add_months(value: datetime, months: int) -> datetime:
    index = value.year * 12 + value.month - 1 + months
    year, month_index = divmod(index, 12)
    return month_start(year, month_index + 1)


def month_range(start: datetime, end: datetime) -> Iterable[tuple[datetime, datetime]]:
    current = month_start(start.year, start.month)
    boundary = month_start(end.year, end.month)
    while current < boundary:
        following = add_months(current, 1)
        yield current, following
        current = following


def engine_from_environment() -> Engine:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL must be set; refusing to use an implicit production database"
        )
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})


def ensure_archive_schema(connection) -> None:
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(ARCHIVE_SCHEMA)}"))


def ensure_traffic_partitions(engine: Engine, start: datetime, months: int) -> list[str]:
    """Create monthly traffic partitions ahead of ingestion."""
    if months < 1 or months > 36:
        raise ValueError("months must be between 1 and 36")
    created: list[str] = []
    end = add_months(start, months)
    with engine.begin() as connection:
        for lower, upper in month_range(start, end):
            name = f"traffic_history_{lower:%Y%m}"
            qname = f"{quote_identifier(SCHEMA)}.{quote_identifier(name)}"
            parent = f"{quote_identifier(SCHEMA)}.{quote_identifier(PARTITION_TABLE)}"
            connection.execute(
                text(
                    f"CREATE TABLE IF NOT EXISTS {qname} PARTITION OF {parent} "
                    "FOR VALUES FROM (:lower) TO (:upper)"
                ),
                {"lower": lower, "upper": upper},
            )
            connection.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS {quote_identifier('ix_' + name + '_zone_time')} ON {qname} (tenant_id, zone_id, observed_at DESC)"
                )
            )
            created.append(name)
    return created


def partition_names_before(cutoff: datetime) -> list[str]:
    """Return only complete monthly partitions strictly before cutoff month."""
    first = month_start(cutoff.year, cutoff.month)
    names: list[str] = []
    # A bounded lookback avoids querying or constructing arbitrary identifiers.
    for months_back in range(1, 121):
        candidate = add_months(first, -months_back)
        names.append(f"traffic_history_{candidate:%Y%m}")
    return names


def archive_traffic(engine: Engine, cutoff: datetime, dry_run: bool = False) -> list[str]:
    """Detach complete monthly partitions and move them into ``archive``."""
    moved: list[str] = []
    candidates = partition_names_before(cutoff)
    inspector = inspect(engine)
    with engine.begin() as connection:
        ensure_archive_schema(connection)
        existing = set(inspector.get_table_names(schema=SCHEMA))
        for name in candidates:
            if name not in existing or name == "traffic_history_default":
                continue
            archived_name = f"{name}_archived"
            if not _IDENTIFIER.fullmatch(archived_name):
                raise ValueError(f"generated archive identifier is unsafe: {archived_name}")
            source = f"{quote_identifier(SCHEMA)}.{quote_identifier(name)}"
            archived = f"{quote_identifier(ARCHIVE_SCHEMA)}.{quote_identifier(archived_name)}"
            if dry_run:
                moved.append(name)
                continue
            connection.execute(
                text(
                    f"ALTER TABLE {quote_identifier(SCHEMA)}.{quote_identifier(PARTITION_TABLE)} DETACH PARTITION {source}"
                )
            )
            connection.execute(
                text(f"ALTER TABLE {source} SET SCHEMA {quote_identifier(ARCHIVE_SCHEMA)}")
            )
            # SET SCHEMA retains the table name; rename only after the move.
            connection.execute(
                text(
                    f"ALTER TABLE {quote_identifier(ARCHIVE_SCHEMA)}.{quote_identifier(name)} RENAME TO {quote_identifier(archived_name)}"
                )
            )
            connection.execute(text(f"ANALYZE {archived}"))
            moved.append(name)
    return moved


DECISION_ARCHIVE_TABLES = (
    "decision_record",
    "decision_candidate",
    "decision_trace",
    "evidence_item",
    "tool_call",
    "scenario_modification",
)


def ensure_decision_archive_tables(connection) -> None:
    """Create archive tables without copying FKs back to live tables."""
    ensure_archive_schema(connection)
    for table in DECISION_ARCHIVE_TABLES:
        source = f"{quote_identifier(SCHEMA)}.{quote_identifier(table)}"
        target = f"{quote_identifier(ARCHIVE_SCHEMA)}.{quote_identifier(table)}"
        connection.execute(
            text(f"CREATE TABLE IF NOT EXISTS {target} AS TABLE {source} WITH NO DATA")
        )
    connection.execute(
        text(
            f"CREATE INDEX IF NOT EXISTS ix_archive_decision_record_created ON {quote_identifier(ARCHIVE_SCHEMA)}.decision_record (created_at DESC)"
        )
    )
    for table in DECISION_ARCHIVE_TABLES[1:]:
        connection.execute(
            text(
                f"CREATE INDEX IF NOT EXISTS {quote_identifier('ix_archive_' + table + '_decision')} ON {quote_identifier(ARCHIVE_SCHEMA)}.{quote_identifier(table)} (decision_id)"
            )
        )


def archive_decisions(engine: Engine, cutoff: datetime, dry_run: bool = False) -> int:
    """Archive old decisions and their lineage children atomically."""
    with engine.begin() as connection:
        ensure_decision_archive_tables(connection)
        count = connection.execute(
            # The schema is constant and identifiers are strictly quoted.
            text(
                f"SELECT count(*) FROM {quote_identifier(SCHEMA)}.decision_record WHERE created_at < :cutoff"  # nosec B608
            ),
            {"cutoff": cutoff},
        ).scalar_one()
        if dry_run:
            return int(count)
        # Archive children first; NOT EXISTS makes retries idempotent.
        predicates = {
            "decision_candidate": "decision_id",
            "decision_trace": "decision_id",
            "evidence_item": "decision_id",
            "tool_call": "decision_id",
            "scenario_modification": "decision_id",
        }
        for table, key in predicates.items():
            source = f"{quote_identifier(SCHEMA)}.{quote_identifier(table)}"
            target = f"{quote_identifier(ARCHIVE_SCHEMA)}.{quote_identifier(table)}"
            connection.execute(
                # Table names come from the fixed DECISION_ARCHIVE_TABLES allowlist.
                text(
                    f"INSERT INTO {target} SELECT s.* FROM {source} s "  # nosec B608
                    f"WHERE EXISTS (SELECT 1 FROM {quote_identifier(SCHEMA)}.decision_record d WHERE d.decision_id = s.{quote_identifier(key)} AND d.created_at < :cutoff) "
                    f"AND NOT EXISTS (SELECT 1 FROM {target} a WHERE a.{quote_identifier(key)} = s.{quote_identifier(key)})"
                ),
                {"cutoff": cutoff},
            )
        connection.execute(
            # Archive/source schemas are constants and identifiers are strictly quoted.
            text(
                f"INSERT INTO {quote_identifier(ARCHIVE_SCHEMA)}.decision_record "  # nosec B608
                f"SELECT s.* FROM {quote_identifier(SCHEMA)}.decision_record s "
                f"WHERE s.created_at < :cutoff AND NOT EXISTS (SELECT 1 FROM {quote_identifier(ARCHIVE_SCHEMA)}.decision_record a WHERE a.decision_id = s.decision_id)"
            ),
            {"cutoff": cutoff},
        )
        for table in predicates:
            connection.execute(
                # Table names come from the fixed decision-lineage allowlist.
                text(
                    f"DELETE FROM {quote_identifier(SCHEMA)}.{quote_identifier(table)} s WHERE EXISTS "  # nosec B608
                    f"(SELECT 1 FROM {quote_identifier(ARCHIVE_SCHEMA)}.decision_record d WHERE d.decision_id = s.decision_id)"
                )
            )
        connection.execute(
            # The schema is constant and identifiers are strictly quoted.
            text(
                f"DELETE FROM {quote_identifier(SCHEMA)}.decision_record WHERE created_at < :cutoff"  # nosec B608
            ),
            {"cutoff": cutoff},
        )
        connection.execute(text(f"ANALYZE {quote_identifier(ARCHIVE_SCHEMA)}.decision_record"))
        connection.execute(text(f"ANALYZE {quote_identifier(SCHEMA)}.decision_record"))
        return int(count)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    ensure = subparsers.add_parser("ensure-partitions")
    ensure.add_argument(
        "--start",
        type=parse_timestamp,
        default=datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    )
    ensure.add_argument("--months-ahead", type=int, default=3)
    for command in ("archive-traffic", "archive-decisions"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--before", type=parse_timestamp, required=True)
        sub.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    engine = engine_from_environment()
    if args.command == "ensure-partitions":
        result = ensure_traffic_partitions(engine, args.start, args.months_ahead)
    elif args.command == "archive-traffic":
        result = archive_traffic(engine, args.before, args.dry_run)
    else:
        result = archive_decisions(engine, args.before, args.dry_run)
    print({"command": args.command, "result": result, "dry_run": getattr(args, "dry_run", False)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
