# OPTIMA-X Phase 3 Optimization Report

## Scope

Phase 3 converts Phase 2 predictions into feasible operational decisions. The implementation keeps prediction, feasibility, and optimization separate: `Prediction` carries demand, ETA, late-risk, and uncertainty; `ConstraintEngine` rejects hard violations; `Objective` scores accepted plans; and `Phase3Solver` provides one comparable solver boundary.

## Implemented components

| Component | Implementation | Validation |
|---|---|---|
| Configurable objective | Distance, fuel, lateness, unserved-order, and vehicle-use weights | Unit test and YAML configuration |
| Hard constraints | Vehicle status, shift, capacity, route/order validity | Structured `ConstraintReport` |
| Assignment | Priority queue and deterministic greedy assignment | ML-to-graph integration test |
| Routing | Existing Dijkstra/A* graph dispatch contract | Existing API and integration tests |
| Local search | 2-opt and 3-opt adapters | Unit tests and experiment runner |
| Metaheuristic | Seeded simulated annealing and genetic search with route repair | Unit tests and comparison experiment |
| DP subproblem | 0/1 knapsack capacity subset selection | Unit test |
| Binary search | Minimum feasible fleet predicate search | Unit test |
| Evaluation | Shared `OptimizationResult` and common objective | Full repository test suite |
| Dashboard | OSM graph, dispatch state, forecast metrics, optimization comparison, sensitivity | Artifact loader checks |

## Experimental design

All route comparisons use the same fixed line graph, same route, same objective function, and seed 42. The generated results are stored in `data/processed/phase3/comparison.json` and `comparison.csv`. A three-stop exact enumeration validates the genetic heuristic against a brute-force optimum. The scalability sweep measures the 2-opt runtime at 10, 25, 50, 100, and 250 stops.

## Measured results

| Algorithm | Objective | Runtime (ms) | Feasible |
|---|---:|---:|---:|
| Greedy | 10.50 | 0.012 | Yes |
| Greedy + 2-opt | 10.50 | 0.045 | Yes |
| Greedy + 3-opt | 10.50 | 0.124 | Yes |
| Simulated annealing | 10.50 | 0.959 | Yes |
| Genetic algorithm | 10.50 | 5.502 | Yes |

The line graph is already ordered, so local search and metaheuristics do not improve objective value. This is an expected workload-specific result, not evidence that the algorithms are equivalent in general. The exact small-instance check found an optimum of 6.15 and the genetic heuristic also returned 6.15.

## Prediction-to-decision sensitivity

The same optimizer was run with actual, naive, XGBoost-like, and intentionally noisy prediction metadata. On this small capacity-saturated fixture, every scenario served one order and left four unserved, producing the same measured decision cost of 412.875. This indicates that the fixture is not sufficiently capacity-flexible to reveal forecast sensitivity; a larger multi-vehicle scenario is required for a meaningful Phase 4-style robustness study. The experiment is still valuable because it establishes the measurement path and prevents unsupported claims about forecast quality translating into operational quality.

## Connectivity review

Phase 1 supplies deterministic simulation models, road graphs, Dijkstra/A*, traffic-aware routing, and dispatch contracts. Phase 2 supplies leakage-safe demand features, XGBoost forecasting, unified TLC/NOAA data preparation, and forecast artifacts. Phase 3 consumes those contracts through `Prediction`, routes orders with the existing graph dispatch router, records a shared `OptimizationResult`, and exposes the generated comparisons through the Streamlit dashboard. The complete validation run passed linting, compilation, the API/system smoke test, and all **30 repository tests** after the Phase 3 additions.

## Reproducibility

Run `python3 scripts/run_phase3_experiments.py` from the repository root. Use seed 42 for all stochastic operators. Run `pytest -q` and `ruff check .` before committing. Large raw data and generated artifacts remain outside the source commit when ignored by repository policy; the experiment code, configuration, report, and tests are versioned.

## Limitations carried forward

The Phase 3 comparison fixture is intentionally small and synthetic, and the current assignment baseline activates at most one order per vehicle dispatch because it preserves the existing single-order graph dispatch mutation contract. Full multi-stop vehicle tours, calibrated ETA models, memory profiling, and broader prediction-error sensitivity belong in the next optimization iteration rather than being claimed as complete here.
