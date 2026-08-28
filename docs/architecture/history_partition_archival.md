# OPTIMA-X Historical Traffic and Decision Archival

**Author:** Karthikeya  
**Implementation:** [`scripts/manage_history.py`](../../scripts/manage_history.py)  
**Schema:** [`src/database/optima_schema.sql`](../../src/database/optima_schema.sql)

## Operating model

`optima.traffic_history` is range-partitioned by `observed_at`. Production creates monthly partitions ahead of ingestion, analyzes each new partition, and detaches only complete partitions older than the retention cutoff. Detached partitions are moved to the `archive` schema and renamed with an `_archived` suffix. The script never detaches the default partition.

Decision records are append-oriented and are archived with their lineage children: candidates, traces, evidence, tool calls, and scenario modifications. These rows are copied into archive tables and then deleted from the live tables within one database transaction. Archive tables are created without foreign keys back to live tables, which allows the live scenario and model rows to be retained independently. The archive is the system of record for cold history and must be included in backup and restore policies.

## Safe scheduler commands

The process requires an explicit `DATABASE_URL`; it refuses to infer a production database. The scheduler account should have only the required schema, table, sequence, and maintenance privileges.

```bash
# Create the current month and the next three monthly partitions.
DATABASE_URL="$OPTIMA_DATABASE_URL" python scripts/manage_history.py \
  ensure-partitions --months-ahead 3

# Preview complete traffic partitions eligible for archival.
DATABASE_URL="$OPTIMA_DATABASE_URL" python scripts/manage_history.py \
  archive-traffic --before 2025-01-01T00:00:00+00:00 --dry-run

# Preview the number of cold decisions and lineage roots.
DATABASE_URL="$OPTIMA_DATABASE_URL" python scripts/manage_history.py \
  archive-decisions --before 2025-01-01T00:00:00+00:00 --dry-run

# Execute archival only after the dry-run output is reviewed.
DATABASE_URL="$OPTIMA_DATABASE_URL" python scripts/manage_history.py \
  archive-traffic --before 2025-01-01T00:00:00+00:00
DATABASE_URL="$OPTIMA_DATABASE_URL" python scripts/manage_history.py \
  archive-decisions --before 2025-01-01T00:00:00+00:00
```

Run partition creation daily or weekly. Run traffic archival after the ingestion watermark has passed the retention boundary and run decision archival during a low-write window. The cutover must be later than the latest expected late-arriving event; otherwise, ingestion will target an archived partition or the default partition.

## Recommended retention tiers

| Data | Hot retention | Archive format | Restore expectation |
|---|---:|---|---|
| Traffic telemetry | 90–180 days | Detached PostgreSQL partitions | Attach or query archive tables for investigations; restore a selected partition into staging. |
| Decision records and lineage | 12–24 months | Archive-schema tables or compressed logical dump | Restore by `decision_id`, scenario, tenant, or time range. |
| Benchmark and RL results | Indefinite or policy-defined | PostgreSQL tables plus object-storage export | Keep immutable experiment artifacts and checksums. |

## Operational safeguards

The script validates timestamps with explicit time zones and strictly validates generated SQL identifiers. It uses half-open monthly bounds, bounded partition discovery, explicit archive names, `ANALYZE` after movement, and transactional decision archival. Archive operations should be preceded by a backup or verified replica checkpoint. After each run, record the command, cutoff, row counts, archive table names, and operator identity in the production change log.

Monitor the following conditions:

| Signal | Meaning | Response |
|---|---|---|
| Rows in `traffic_history_default` | Missing future partition or invalid ingestion timestamp | Create the correct partition and reconcile default rows before archival. |
| Archive row count differs from deleted count | Incomplete or repeated archive operation | Stop deletion jobs and reconcile by primary/foreign lineage keys. |
| Live table size does not fall after archival | Vacuum or long-running transaction delay | Inspect `pg_stat_activity`, wait events, and autovacuum progress. |
| Partition creation failure | Scheduler, privilege, or DDL issue | Alert before the next ingestion window; do not silently continue. |
| Duplicate archive conflict | Partial previous run or manual intervention | Run a reconciliation query; do not use destructive force flags. |

## Restore procedure

For traffic, restore a detached partition into a staging schema first, validate its lower and upper time bounds, row count, checksum sample, and tenant distribution, then attach it to a compatible partitioned table only if the live table has no overlapping rows. For decisions, restore the root table before its child tables if a live rehydration is required, or query archive tables directly for investigations. Rehydration must preserve the original UUIDs and timestamps, and should be performed with foreign-key checks and row-count validation in a controlled migration.

Example traffic inspection:

```sql
SELECT min(observed_at), max(observed_at), count(*), count(DISTINCT tenant_id)
FROM archive.traffic_history_202401_archived;
```

Example decision lineage lookup across hot and cold data should be implemented as an explicit `UNION ALL` view only when needed. Do not make every operational request scan archive tables; keep cold-history queries opt-in.

## SQLAlchemy mapping notes

[`src/database/orm_models.py`](../../src/database/orm_models.py) maps the partitioned traffic table with a composite `(traffic_id, observed_at)` key and declares the principal DDL indexes for traffic and decision queries. SQLAlchemy models do not create or rotate partitions automatically. Partition lifecycle remains an explicit operational concern handled by the CLI or a migration/scheduler job, preventing an application request from unexpectedly executing DDL.
