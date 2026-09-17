# Java and PostgreSQL Visibility in OPTIMA-X

**Author: Karthikeya**

OPTIMA-X uses Python for orchestration, machine learning, simulation, and the FastAPI surface. The Java module is not a placeholder: `java-dsa` provides a language-independent reference layer for shortest paths and optimization structures. Its `RoadGraph` and `ShortestPaths` classes implement deterministic Dijkstra and A* contracts, while Maven/JUnit tests verify cost parity, admissible heuristics, and invalid negative-edge rejection. This reference layer makes the algorithmic contribution reviewable independently from the Python runtime.

PostgreSQL is the persistent lineage layer for all seven phases. The canonical DDL in `src/database/optima_schema.sql` defines 28 tables, including operational state, demand and ETA predictions, optimization outputs, reinforcement-learning episodes, decision evidence, runtime events, and benchmark results. `traffic_history` and `decision_record` are partitioned for historical scale. The `decision_lineage` view joins optimization, candidate, trace, and evidence counts so a Phase 7 benchmark can be traced back to the decision it evaluated.

The public endpoint `/api/v1/architecture/implementation-visibility` exposes these boundaries to the TypeScript dashboard. It reports the Java source and test paths, PostgreSQL engine and partitioned tables, the lineage view, and the Phase 1–7 contract chain without exposing tenant data.

## Verification commands

```bash
mvn -q -f java-dsa/pom.xml test
python -m pytest -q tests/test_neural_trace.py tests/integration/test_database_lifecycle.py
```

The database lifecycle test remains container-dependent. When PostgreSQL is unavailable, CI should report the environment limitation rather than treating an unexecuted integration path as a passing database validation.
