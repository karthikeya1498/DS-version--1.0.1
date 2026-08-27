# OPTIMA-X language architecture correction

**Author: Karthikeya**

The project uses an intentionally controlled stack. Python remains the primary language for data engineering, ML forecasting, simulation, optimization orchestration, reinforcement learning, LLM tooling, and FastAPI. Java is now explicit for the interview-oriented DSA layer: weighted road graphs, Dijkstra, A*, heaps, union-find, knapsack dynamic programming, and deterministic algorithm benchmarks. SQL remains the persistence and analytical-query language.

The Python DSA package remains available because the production Python optimization and API layers already depend on it. The Java module is a comparable reference and benchmark implementation, not an unsafe rewrite that would break existing orchestration. The boundary is value-oriented: Java emits deterministic path and metric records, while Python owns cross-layer application decisions.

| Responsibility | Language | Evidence |
|---|---|---|
| Data, ML, simulation, optimization, RL, LLM, API | Python | Existing `src/`, `api/`, scripts, and pytest suite |
| Explicit DSA and algorithm benchmarks | Java | `java-dsa/src/main/java/com/optimax/dsa` and JUnit tests |
| Persistence, joins, constraints, analytics | SQL | `src/database/schema.sql` |
| Configuration and CI | YAML/Bash | `configs/` and `.github/workflows/` |

Comments were added where they explain algorithmic intent, invariants, complexity, safety boundaries, or interoperability. Repeating a comment on every trivial assignment would reduce readability and is not professional documentation.
