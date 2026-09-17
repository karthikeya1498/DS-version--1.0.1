# Phase 7 Prediction-to-Decision Benchmark

**Author:** Karthikeya  
**Dataset:** UCI Bike Sharing hourly demand  
**Fixed optimizer:** `Phase3Solver` with Greedy assignment and A* routing  
**Seed:** 42

## Research question

> Does better predictive accuracy necessarily produce better downstream logistics decisions?

The benchmark keeps the chronological test period, fixed graph, order set, vehicle fleet, optimizer, objective weights, and seed constant. Only the prediction source or controlled error treatment changes.

## Executed command

```bash
python3 scripts/run_prediction_decision_benchmark.py \
  --epochs 20 \
  --window 24 \
  --output data/processed/phase7_prediction_decision.json
```

The benchmark evaluated XGBoost, MLP, and LSTM demand predictions under clean, +5%, +10%, +20%, and priority-targeted error treatments. It recorded prediction MAE/RMSE and decision cost, distance, lateness, service counts, feasibility, and optimizer runtime for every row.

## Observed prediction results

| Model | Clean MAE | Clean RMSE | Interpretation |
|---|---:|---:|---|
| XGBoost | 184.92 | 213.33 | Tabular baseline. |
| MLP | 184.80 | 208.88 | Slightly lower error than XGBoost in this run. |
| LSTM | 149.25 | 164.17 | Best prediction metrics in this run. |

The noise treatments increased MAE and RMSE monotonically for each model. For example, LSTM RMSE increased from 164.17 clean to 173.32 at +5%, 182.54 at +10%, and 201.17 at +20%.

## Downstream results and interpretation

The fixed scenario served 2 orders and left 3 unserved, with a feasible selected route set and zero measured lateness. The decision cost was 327.25 and distance was 6.90 km across the observed treatments in this run. This invariant operational result is not evidence that predictions do not matter; it indicates that this particular scenario is dominated by the fleet-capacity bottleneck and the available route geometry. Prediction changes did not cross the assignment boundary.

That result is itself useful for experimental design. A stronger second benchmark should increase fleet capacity, include multiple vehicles with closer route-cost alternatives, add deadline-sensitive ETA/late-risk predictions, and evaluate enough scenarios to observe assignment changes. The benchmark artifact must retain both the invariant result and the scenario limitations instead of manufacturing a difference.

## Reproducibility and next experiment

The JSON artifact is `data/processed/phase7_prediction_decision.json`. Before drawing a general conclusion, run paired scenarios across multiple seeds and use an operationally sensitive fleet configuration. The next experiment should report paired cost deltas, lateness deltas, unserved-order deltas, bootstrap confidence intervals, and the fraction of scenarios in which the best predictive model is also the best decision model.
