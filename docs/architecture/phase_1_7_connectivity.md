# OPTIMA-X Phase 1–7 Connectivity Contract

**Author:** Karthikeya  
**Status:** Architecture contract for implementation and validation

## System loop

OPTIMA-X follows one reproducible chain rather than seven disconnected demonstrations:

> **Operational world → prediction → constrained optimization → sequential policy → decision intelligence → production telemetry → scientific evidence → feedback into the next experiment.**

Every executable scenario is identified by a scenario ID, data version, configuration version, algorithm version, and seed. PostgreSQL provides the durable lineage layer; filesystem artifacts hold large benchmark outputs and charts; the API exposes controlled operational contracts; the TypeScript console visualizes status and live events.

| Phase | Input | Canonical output | Persistence | Validation focus |
|---|---|---|---|---|
| 1 — World | Dataset version, graph, fleet, orders, traffic, seed | `OperationalState` | `scenario`, graph tables, `logistics_order`, `vehicle`, `traffic_history` | Dijkstra/A*, graph reachability, reproducible simulation |
| 2 — Forecast | Operational state and feature version | `PredictionBundle` | `model_version`, `demand_prediction`, `eta_prediction` | Time-aware splits, MAE/RMSE, late-risk calibration, leakage control |
| 3 — Optimize | State, predictions, objective and constraints | `OptimizationResult` | `optimization_run`, `route_assignment`, `route_stop` | Feasibility, objective value, lateness, unserved orders, runtime |
| 4 — Learn | State transitions and rewards | `PolicyOutcome` | `rl_experiment`, `rl_episode`, `rl_step` | Paired seeds, held-out scenarios, robustness, hybrid fallback |
| 5 — Explain | Prediction, optimization, and policy outputs | `DecisionRecord` | Decision lineage, evidence, traces, tools, modifications | Evidence grounding and counterfactual consistency |
| 6 — Operate | API requests, model versions, traffic events | `RuntimeTelemetry` | `system_event`, traffic history, CI artifacts | Security, latency, memory, WebSocket stability, regression gates |
| 7 — Prove | Versioned outputs from Phases 1–6 | `BenchmarkEvidence` | `benchmark_run` and immutable research artifacts | Ablation, scalability, distribution shift, statistical comparison |

## Traceability requirements

A benchmark row must be sufficient to reproduce its result without relying on screenshots or copied console output. At minimum, it records the scenario/data version, algorithm and model versions, feature version, objective configuration, constraint configuration, seed policy, runtime environment, metrics, feasibility, and artifact paths or checksums.

The mandatory lineage is:

```text
Scenario/Data Version
  → OperationalState
  → PredictionBundle
  → OptimizationResult
  → PolicyOutcome
  → DecisionRecord + Evidence
  → RuntimeTelemetry
  → BenchmarkEvidence
  → Statistical Analysis
```

Prediction-error propagation must hold the scenario and optimization configuration fixed while perturbing demand or ETA predictions at controlled levels. RL evaluation must keep training, tuning, and final test scenarios separate. Heuristic quality must be compared to exact small-instance results where feasible. Final reports must distinguish local measurements from deployed-equivalent and production-scale claims.

## API and frontend connection

The dashboard consumes three public contracts:

| Contract | Endpoint | Frontend use |
|---|---|---|
| Scenario execution | `POST /api/v1/simulation/run` | Updates operational metrics and decision trace. |
| Phase connectivity | `GET /api/v1/architecture/status` | Adds contract/persistence tooltips to all seven phase cards. |
| Live traffic | `WebSocket /api/v1/ws/traffic` | Streams authenticated route re-optimization events with reconnect handling. |

The frontend is intentionally dependency-light. It uses an inline SVG road-network graphic, CSS-generated telemetry bars, semantic sections, keyboard-visible focus states, responsive layouts, and a persisted `optima-theme` preference for dark and light modes. The API status request is additive and fails gracefully so the visual shell remains usable during service outages.

## PostgreSQL boundary

PostgreSQL is not called directly by the browser. Python orchestration and API routes own database access through SQLAlchemy; Alembic owns schema evolution; the history-management CLI owns partition creation and cold archival. The browser receives bounded response DTOs and never receives database credentials or arbitrary SQL identifiers.

## Research validation controls

The Phase 7 plan requires controlled comparisons rather than universal algorithm claims. The implementation must preserve identical scenarios and objective definitions when comparing Dijkstra with A*, baselines with XGBoost, Greedy with local search, deterministic optimization with RL, and standalone policies with the hybrid fallback. Stochastic methods require multiple predefined seeds and paired scenario sets. Metrics should report central tendency and spread, while failure analysis records infeasibility, timeouts, data-quality issues, drift, and explanation-grounding failures.

## Definition of done

A complete evaluation environment can create a reproducible scenario, materialize an operational state, generate versioned predictions, produce constrained routing, evaluate sequential policies, persist an evidence-grounded decision, stream runtime telemetry, and execute a benchmark that reports provenance and uncertainty. The final conclusion must explain which component caused an observed difference, the computational cost, stability under perturbation, and conditions under which a simpler method is preferable.
