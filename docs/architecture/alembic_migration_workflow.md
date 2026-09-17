# OPTIMA-X Alembic Migration Workflow

**Author:** Karthikeya  
**Configuration:** [`alembic.ini`](../../alembic.ini)  
**Environment:** [`alembic/env.py`](../../alembic/env.py)  
**Baseline:** [`20260828_01_canonical_optima_schema.py`](../../alembic/versions/20260828_01_canonical_optima_schema.py)

## Purpose

Alembic is the controlled schema-evolution mechanism for the 28 mapped tables in the `optima` schema. The SQLAlchemy metadata remains the application mapping contract, while Alembic revisions are the deployment contract. A migration revision is immutable after it has reached a shared environment; future changes must be represented by a new revision.

The initial revision installs the reviewed [`src/database/optima_schema.sql`](../../src/database/optima_schema.sql) artifact. This makes adoption reproducible without copying the DDL into a second, divergent source. Later revisions should use explicit `op.add_column`, `op.create_index`, `op.create_table`, partition operations, and data backfills with clearly bounded transactions.

## Seven-phase ownership

| Phase | Migration ownership | Typical future migration |
|---|---|---|
| 1 | `tenant`, `dataset_version`, `scenario`, graph, fleet, orders, traffic, weather | Add a validated operational attribute or a new partition policy. |
| 2 | `model_version`, `demand_prediction`, `eta_prediction` | Add prediction calibration fields or a feature-manifest reference. |
| 3 | `optimization_run`, `route_assignment`, `route_stop` | Add solver diagnostics or route execution status. |
| 4 | `rl_experiment`, `rl_episode`, `rl_step` | Add evaluation cohort or policy-checkpoint metadata. |
| 5 | `decision_record`, candidates, traces, evidence, tools, modifications | Add lineage fields, immutable status controls, or explanation metadata. |
| 6 | `system_event` and operational indexes | Add correlation, retention, or observability dimensions. |
| 7 | `benchmark_run` | Add a benchmark metric or statistical-comparison dimension. |

## Developer workflow

```bash
# Install the database extra.
pip install -e '.[database]'

# Point Alembic at a disposable PostgreSQL 16 database.
export DATABASE_URL='postgresql+psycopg://optima:optima@localhost:5432/optima_test'

# Inspect and apply migrations.
alembic current
alembic history
alembic upgrade head

# Generate SQL for review without applying it.
alembic upgrade head --sql > /tmp/optima_upgrade.sql

# Create a new revision only after the ORM and migration design are reviewed.
alembic revision -m 'add decision approval timestamp'

# Validate downgrade in a disposable database.
alembic downgrade base
alembic upgrade head
```

Autogeneration is not a substitute for review. Use `alembic revision --autogenerate` as a diff assistant only, then inspect the revision for PostgreSQL-specific details such as partition bounds, partial indexes, concurrent index creation, data backfills, foreign-key lock behavior, and nullable-to-non-nullable transitions.

## CI workflow

The Python GitHub Actions job starts a PostgreSQL 16 service container, installs the database extra, runs `alembic upgrade head`, executes `pytest -m integration`, runs the remaining tests, and finally runs Ruff. A migration failure blocks the rest of the database integration gate. The container database is disposable and never contains production credentials.

## Production rollout rules

Migrations run as a dedicated release step with a least-privilege deployment role. The application role should not have arbitrary DDL privileges. Before applying a migration, capture a backup or confirm a recoverable replica checkpoint, inspect lock duration and table size, and verify the migration’s expected statement timeout. Large indexes should be created with `CONCURRENTLY` in a separately managed, non-transactional migration step. Partition creation should be scheduled before ingestion, while partition detach/archive is handled by [`scripts/manage_history.py`](../../scripts/manage_history.py).

For high-risk changes, use an expand/contract sequence: add nullable structures first, deploy code that can read both versions, backfill in bounded batches, validate counts and constraints, switch reads/writes, and remove the old structure in a later revision. Never edit an applied revision and never use `DROP ... CASCADE` outside disposable downgrade validation.

## Verification checklist

| Check | Required evidence |
|---|---|
| Upgrade | `alembic upgrade head` completes against a clean PostgreSQL 16 database. |
| ORM alignment | `Base.metadata` contains 28 mapped tables and expected composite/partial indexes. |
| Integration behavior | Container tests cover inserts, relationships, traffic partition movement, and decision-lineage archival. |
| Downgrade | Baseline downgrade succeeds only in disposable environments. |
| SQL review | Generated SQL and lock impact are reviewed before production. |
| Rollback | Backup/restore or forward-fix procedure is documented for the revision. |

## References

[1]: https://alembic.sqlalchemy.org/en/latest/tutorial.html "Alembic official tutorial"

[2]: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html "SQLAlchemy 2.0 declarative table mapping"
