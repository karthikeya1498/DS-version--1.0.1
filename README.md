# OPTIMA-X

**Author: Karthikeya**

OPTIMA-X is an end-to-end urban logistics decision-optimization engine. It combines machine-learning demand and ETA forecasting, graph algorithms, vehicle routing, reinforcement learning, PostgreSQL lineage, and explainable decision intelligence in one traceable pipeline.

> **Predict demand → estimate ETA → assign orders → optimize routes → evaluate late-delivery risk → explain the decision → measure the outcome.**

## Why this project is credible

OPTIMA-X is organized as an executable research and engineering system rather than a collection of isolated notebooks. The Python service owns orchestration and forecasting, the Java module provides an independent DSA reference implementation, PostgreSQL stores operational and experiment lineage, and the TypeScript dashboard exposes live system state and real neural activations.

The current implementation covers eight connected phases:

| Phase | Capability | Evidence |
|---:|---|---|
| 1 | Operational state and simulation | `src/simulation`, domain tests |
| 2 | Feature engineering and forecasting | XGBoost pipeline and temporal evaluation |
| 3 | Routing and constrained optimization | Dijkstra, A*, dispatch, multi-stop assignment |
| 4 | PPO/RL policy experiments | `src/rl`, seeded evaluation artifacts |
| 5 | Decision intelligence and explanations | decision records, traces, evidence |
| 6 | Production engineering | FastAPI, WebSocket traffic, PostgreSQL ORM/migrations |
| 7 | Research validation | prediction-to-decision and multi-seed studies |
| 8 | Operational intelligence | readiness, request metrics, dashboard reliability cards |

## Verified quantitative results

The UCI Bike Sharing hourly benchmark uses a chronological 80/20 split with **17,389 observations**. On the documented feature set, XGBoost achieved **MAE 43.289, RMSE 66.985, and R² 0.908**, compared with the seasonal-mean baseline at **MAE 174.985 and RMSE 232.608**. That is a **75.3% lower MAE** and **71.2% lower RMSE** than the baseline.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Seasonal mean baseline | 174.985 | 232.608 | -0.113 |
| Gradient Boosting | 73.617 | 107.438 | 0.763 |
| Random Forest | 45.622 | 70.261 | 0.898 |
| **XGBoost** | **43.289** | **66.985** | **0.908** |

The graph benchmark found identical Dijkstra and A* path costs across the tested deterministic grids. With the current uncalibrated coordinate heuristic, A* was **1.33–1.50× slower** and visited **1.16–1.23× more nodes** than Dijkstra. This is reported as an implementation diagnostic, not as a claim that A* is universally inferior.

These numbers are documented in the [benchmark and forecasting report](docs/research/benchmark_and_forecasting_report.md). The research caveat is intentional: the current XGBoost result is a strong tabular baseline, not a deployment claim, and future evaluation should add rolling features, explicit weather interactions, prediction intervals, and production drift checks.

## Repository structure

```text
api/                    FastAPI routes, authentication, realtime APIs
frontend/               TypeScript/Vite operations dashboard
java-dsa/               Java 21 Dijkstra, A*, heap, union-find, and tests
src/database/           PostgreSQL schema, ORM models, migrations, repositories
src/ml/                 Demand, ETA, late-risk, and neural forecasting
src/optimization/       Assignment, routing, constraints, and objectives
src/rl/                  PPO/DQN environments and evaluation
scripts/                Reproducible training, benchmark, and validation runners
data/                   Small tracked manifests and derived research artifacts
docs/                   Architecture, research, reports, reviews, and design notes
tests/                  Unit, integration, API, database, ML, routing, and RL tests
```

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,ml,database]'
pytest -q
uvicorn api.main:app --reload
```

The API documentation is available at `http://localhost:8000/docs`. Build the dashboard with:

```bash
npm --prefix frontend install
npm --prefix frontend run build
```

## Important endpoints

| Endpoint | Purpose |
|---|---|
| `/api/v1/health` | Basic service health |
| `/api/v1/architecture/status` | Phase 1–8 contract status |
| `/api/v1/neural/trace` | Real neural features, weights, activations, and prediction |
| `/api/v1/operations/readiness` | PostgreSQL configuration and operational readiness |
| `/api/v1/operations/metrics` | Route-level request and latency metrics |
| `/api/v1/traffic/ws` | Realtime traffic and route updates |

## Documentation

- [Documentation index and contribution guide](docs/README.md)
- [Architecture overview](docs/architecture/full_architecture.md)
- [PostgreSQL schema and performance](docs/architecture/postgresql_schema_and_performance.md)
- [Java and PostgreSQL visibility](docs/architecture/java-postgresql-visibility.md)
- [Benchmark and forecasting report](docs/research/benchmark_and_forecasting_report.md)
- [Neural prediction research](docs/research/neural_prediction.md)
- [Complete project report](docs/reports/optimax_complete_project_report.md)
- [Phase 8 operational intelligence](docs/research/phase8_operational_intelligence.md)

## Status

The repository is an active research-grade implementation. CI validates Python, Java, frontend security, Docker, database lifecycle, and Phase 8 operational contracts. Production deployment still requires a managed PostgreSQL instance, secrets configuration, and representative load validation.
