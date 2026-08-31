# OPTIMA-X PostgreSQL Schema and Performance Design

**Author:** Karthikeya  
**Status:** Architecture draft for implementation review  
**Database target:** PostgreSQL 16+

## 1. Architectural role

PostgreSQL is the durable integration layer between the seven OPTIMA-X phases. Computational components may operate in memory, but every externally meaningful input, prediction, route, policy result, decision, explanation, event, and experiment result can be persisted with tenant, scenario, version, timestamp, and provenance identifiers. This creates a reproducible lineage from raw operational state to an executed or rejected decision.

The canonical additive DDL is in [`src/database/optima_schema.sql`](../../src/database/optima_schema.sql), while the Mermaid relationship model is in [`optima_postgresql_er.mmd`](optima_postgresql_er.mmd). The existing `src/database/schema.sql` remains unchanged as a legacy Phase 1 compatibility schema; production migration should introduce the `optima` schema and backfill data explicitly rather than silently renaming live tables.

## 2. Phase-to-table mapping

| Phase | Responsibility | Primary PostgreSQL relations | Persistence contract |
|---|---|---|---|
| Phase 1 — operational foundation | Tenancy, datasets, scenarios, orders, fleet, locations, road graph, traffic, weather | `tenant`, `dataset_version`, `scenario`, `location`, `vehicle`, `vehicle_shift`, `logistics_order`, `road_node`, `road_edge`, `traffic_history`, `weather_observation` | Inputs are validated, timestamped, and linked to a scenario or immutable dataset manifest. |
| Phase 2 — forecasting | Demand, ETA, late-risk models and predictions | `model_version`, `demand_prediction`, `eta_prediction` | Every prediction records model version, feature version, generation time, forecast horizon, and scenario context. |
| Phase 3 — optimization | Solver runs, vehicle assignments, ordered route stops | `optimization_run`, `route_assignment`, `route_stop` | Objective values, feasibility, solver version, and route alternatives remain queryable after execution. |
| Phase 4 — RL | PPO experiment configuration, episodes, states, actions, rewards, seeds | `rl_experiment`, `rl_episode`, `rl_step` | Paired scenarios, seeds, policy versions, rewards, win rates, and runtimes support reproducible evaluation. |
| Phase 5 — decision intelligence | Decision records, candidates, traces, evidence, tool calls, counterfactual scenarios | `decision_record`, `decision_candidate`, `decision_trace`, `evidence_item`, `tool_call`, `scenario_modification`, `decision_lineage` | A decision points to the scenario, models, optimization result, RL episode, selected action, alternatives, evidence, and code commit. |
| Phase 6 — production engineering | Operational events, correlation IDs, latency and component history | `system_event`, plus timestamps and latency fields across trace/run tables | Observability records are append-oriented and queryable by component, correlation, tenant, and time. |
| Phase 7 — research evaluation | Benchmark runs and statistical comparison metadata | `benchmark_run`, `rl_experiment`, `scenario`, `dataset_version` | Algorithm version, scenario, seed, runtime, objective, lateness, feasibility, and arbitrary metrics are retained for ablations and regressions. |

## 3. Core integrity rules

Every tenant-owned relation carries `tenant_id`; application queries must scope by tenant before applying user-supplied filters. A scenario is the reproducibility boundary and contains a seed, configuration, dataset reference, and time range. Dataset content is identified by a SHA-256 manifest, while model and feature versions are separate so a prediction cannot be mistaken for a model-only artifact.

All event times use `timestamptz`. The application must write UTC and must not use local wall-clock strings as ordering keys. `CHECK` constraints reject negative capacities, distances, durations, probabilities, multipliers, and invalid windows. The `vehicle_shift` exclusion constraint prevents overlapping shifts for the same vehicle. The `scenario_modification` constraint guarantees that a what-if request cannot mutate its baseline scenario.

The `decision_record` is deliberately an immutable-style append record. Corrections should create a new record with a superseding relationship in application metadata rather than updating historical evidence. A database trigger can enforce immutability after `status = 'executed'` in a later migration. JSONB is reserved for variable-shaped model outputs, action payloads, metrics, and evidence values; high-selectivity fields needed for joins and filters remain typed columns.

## 4. DecisionRecord indexing strategy

The principal access pattern is tenant-scoped retrieval of decisions for a scenario in reverse chronological order:

```sql
SELECT d.*
FROM optima.decision_record AS d
WHERE d.tenant_id = $1
  AND d.scenario_id = $2
  AND d.created_at >= $3
  AND d.created_at <  $4
ORDER BY d.created_at DESC
LIMIT $5;
```

The covering shape is `(tenant_id, scenario_id, created_at DESC)`. Tenant is first because it is a mandatory isolation predicate, scenario is second because it is the primary lineage filter, and descending creation time supports the ordering and early stop for a bounded page. The index is already declared as `ix_decision_tenant_scenario_time`.

Operational dashboards commonly ask for recent proposed or executed decisions. The partial-compatible shape `(tenant_id, status, created_at DESC)` is declared as `ix_decision_tenant_status_time`. If production measurements show that only one status is queried repeatedly, add a narrower partial index, for example `WHERE status IN ('proposed','approved')`; do not add several status-specific indexes without measuring write and vacuum cost.

Foreign-key lookup indexes exist for optional links to optimization runs and RL episodes. They are partial because null values do not participate in those lookups. Candidate, trace, and evidence tables use `(decision_id, time)` or `(decision_id, rank)` indexes so the API can load a decision trace without scanning unrelated records. The `decision_lineage` view uses grouped counts for convenience; for high-volume dashboards, replace repeated aggregation with a maintained summary table or a request-specific query to avoid counting the same one-to-many joins repeatedly.

### Recommended DecisionRecord queries

```sql
-- Latest decision with its alternatives and evidence.
SELECT d.decision_id, d.created_at, d.algorithm, d.selected_action,
       c.rank, c.feasible, c.objective_metrics,
       e.evidence_type, e.claim, e.value
FROM optima.decision_record d
LEFT JOIN optima.decision_candidate c ON c.decision_id = d.decision_id
LEFT JOIN optima.evidence_item e ON e.decision_id = d.decision_id
WHERE d.tenant_id = $1 AND d.scenario_id = $2
ORDER BY d.created_at DESC, c.rank ASC, e.captured_at DESC
LIMIT $3;
```

For this endpoint, first fetch the page of decision IDs, then fetch children with `WHERE decision_id = ANY($1)` if a decision can have many candidates or evidence items. This avoids multiplying candidate rows by evidence rows and prevents an unnecessarily large join result.

```sql
-- Use the planner, not intuition, to verify the production plan.
EXPLAIN (ANALYZE, BUFFERS, SETTINGS)
SELECT decision_id, status, created_at
FROM optima.decision_record
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND scenario_id = '00000000-0000-0000-0000-000000000002'
ORDER BY created_at DESC
LIMIT 50;
```

The expected plan for a selective query is an index scan on `ix_decision_tenant_scenario_time` with little or no explicit sort. Investigate regressions when the plan switches to a sequential scan, when heap fetches dominate, when rows removed by filter are large, or when estimates diverge materially from actual rows.

## 5. Traffic-history indexing and storage strategy

Traffic history is append-heavy, time-series data. The canonical table is range-partitioned by `observed_at` and includes a default partition only as a safety net. Production should create monthly or weekly partitions ahead of ingestion and monitor the default partition; rows in the default partition indicate a partition-management defect. Retention can then detach or archive old partitions instead of issuing a large delete.

The main zone-window query is:

```sql
SELECT zone_id, observed_at, multiplier, speed_kph, congestion_level
FROM optima.traffic_history
WHERE tenant_id = $1
  AND zone_id = $2
  AND observed_at >= $3
  AND observed_at <  $4
ORDER BY observed_at DESC
LIMIT $5;
```

`ix_traffic_tenant_zone_time (tenant_id, zone_id, observed_at DESC)` supports tenant isolation, zone filtering, time-range pruning within the partition, and reverse chronological retrieval. The edge query uses `ix_traffic_edge_time (edge_id, observed_at DESC)`. Scenario replay uses `ix_traffic_scenario_time (scenario_id, observed_at DESC)`. Do not add indexes on low-cardinality `source`, `multiplier`, or `congestion_level` unless measured workload demonstrates a real selective predicate.

Partition pruning is the first optimization: always express time filters directly on `observed_at` with half-open bounds. Avoid wrapping the partition key in `date(observed_at)`, timezone conversion, or an arbitrary function in the predicate. Use a UTC range such as `[start, end)` and let the client calculate calendar boundaries. Prepared statements should retain typed `timestamptz` parameters so PostgreSQL can plan pruning correctly.

For very large, naturally ordered historical partitions, evaluate a BRIN index on `observed_at` or `(tenant_id, observed_at)` as a low-maintenance complement. BRIN is appropriate when physical row order correlates with time; it is not a replacement for the B-tree used by selective tenant-zone dashboard reads. Keep the B-tree only when it is justified by observed query latency, since every additional index increases ingestion, vacuum, storage, and cache pressure.

## 6. Query-performance operating procedure

Use `EXPLAIN (ANALYZE, BUFFERS)` against representative data volumes, not a tiny development database. Compare cold-cache and warm-cache behavior, record planning and execution time, and capture rows examined versus rows returned. Enable `pg_stat_statements` in managed or production PostgreSQL to rank queries by total time, mean time, calls, shared blocks read, and shared blocks hit. Index decisions should follow those measurements.

Use keyset pagination for both tables. A stable decision page can use `(created_at, decision_id) < ($cursor_time, $cursor_id)` instead of a large `OFFSET`; traffic history can use `(observed_at, traffic_id) < ($cursor_time, $cursor_id)`. This avoids progressively scanning and discarding older rows. The primary key on partitioned traffic history includes both `traffic_id` and `observed_at`, which also supplies a deterministic tie-breaker.

Use connection pooling with bounded pool size, short statement timeouts for dashboard requests, and transaction timeouts for write paths. Keep transactions short and avoid holding a transaction open while calling ML, routing, or external services. Batch telemetry inserts with `COPY` or bounded multi-row inserts. For traffic ingestion, deduplicate at the producer or with a staging table before inserting into the append-only history.

Run `ANALYZE` after large backfills and after creating new partitions. Tune autovacuum more aggressively for hot operational tables and less aggressively for immutable historical partitions. Monitor index hit rate, dead tuples, table and index bloat, partition row counts, default-partition rows, lock waits, and replication lag. Build large new indexes with `CREATE INDEX CONCURRENTLY` in a migration process that is allowed to run outside a transaction.

## 7. Migration and rollout sequence

The DDL is additive and should be introduced in the following order:

1. Create extensions, the `optima` schema, tenancy, datasets, scenarios, locations, and graph tables.
2. Create operational tables and traffic partitions before enabling ingestion.
3. Create model, optimization, RL, and decision-intelligence tables.
4. Backfill from legacy tables using explicit mapping tables; preserve legacy IDs in metadata during reconciliation.
5. Validate row counts, foreign-key coverage, timestamp ranges, tenant ownership, and checksum manifests.
6. Create indexes concurrently for large existing relations and run `ANALYZE`.
7. Switch reads behind a feature flag, compare query plans and latency, then switch writes.
8. Keep the legacy schema read-only through one retention window before decommissioning it.

## 8. References

[1]: https://www.postgresql.org/docs/current/indexes-multicolumn.html "PostgreSQL current documentation: Multicolumn Indexes"

[2]: https://www.postgresql.org/docs/current/indexes-partial.html "PostgreSQL current documentation: Partial Indexes"

[3]: https://www.postgresql.org/docs/current/ddl-partitioning.html "PostgreSQL current documentation: Table Partitioning"

[4]: https://www.postgresql.org/docs/current/using-explain.html "PostgreSQL current documentation: Using EXPLAIN"

[5]: https://www.postgresql.org/docs/current/monitoring-stats.html "PostgreSQL current documentation: Monitoring Database Activity"
