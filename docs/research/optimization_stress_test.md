# Phase 3 Optimization Stress Test

**Author:** Karthikeya  
**Scenario:** 50-order batch with 50-unit vehicle capacity  
**Seed:** 42

## Workload

The stress harness uses a deterministic 51-node road graph, 50 orders, ten vehicles, 50 capacity units per vehicle, 12-hour shifts, and the existing Phase 3 `Phase3Solver` with A* dispatch routing. The same order template, prediction map, objective, graph, and fleet configuration are recreated for every route strategy.

```bash
python3 scripts/run_optimization_stress.py \
  --orders 50 \
  --fleet-capacity 50 \
  --vehicles 10 \
  --output data/processed/phase3_optimization_stress.json
```

## Results

| Strategy | Runtime (ms) | Decision cost | Distance (km) | Lateness (min) | Served | Unserved | Feasible |
|---|---:|---:|---:|---:|---:|---:|---|
| Greedy | 1.468 | 7,532.875 | 293.15 | 275 | 10 | 40 | Yes |
| Greedy + 2-opt | 1.376 | 7,532.875 | 293.15 | 275 | 10 | 40 | Yes |
| Greedy + 3-opt | 1.469 | 7,532.875 | 293.15 | 275 | 10 | 40 | Yes |
| Simulated annealing | 1.562 | 7,532.875 | 293.15 | 275 | 10 | 40 | Yes |
| Genetic | 1.401 | 7,532.875 | 293.15 | 275 | 10 | 40 | Yes |

The measured runtime ranged from 1.376 ms to 1.562 ms for this in-memory workload. The stress run completed without infeasible routes or runtime errors.

## Interpretation

The test served exactly one order per vehicle despite 50 units of capacity per vehicle. This reveals an important current-engine behavior: the existing Phase 3 assignment path is effectively dispatching one order per vehicle in this scenario, so the 500-unit nominal fleet capacity is not being utilized as multi-stop route capacity. The 40 unserved orders are therefore a capacity/assignment-policy result rather than a graph-search failure.

All five reported strategies produced identical outcomes because the current `Phase3Solver.solve` path delegates assignment to the Greedy solver and does not yet apply route-order improvement strategies to the multi-order assignment result. The stress artifact records this honestly instead of implying that the five methods were operationally distinct.

The next engineering improvement should separate order-to-vehicle assignment from route sequencing, allow a vehicle to accumulate compatible orders up to capacity, and invoke 2-opt, 3-opt, simulated annealing, or genetic improvement on the resulting multi-stop routes. A follow-up stress test should then compare throughput, route quality, lateness, and runtime as order volume scales from 50 to 1,000.

The raw result is stored in `data/processed/phase3_optimization_stress.json`, and the runner is `scripts/run_optimization_stress.py`.
