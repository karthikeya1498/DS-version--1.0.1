# A* Calibration, Lagged Forecasting, and ML-to-Routing Integration

## A* on irregular obstacle networks

The obstacle benchmark uses deterministic square grids with approximately 17–18% blocked nodes, bidirectional positive edge weights, and a fixed start/goal pair. Dijkstra provides the optimal reference. A* is evaluated with the original raw coordinate heuristic and a calibrated scale of `grid_side - 1`, which matches normalized coordinate distance to approximately one cost unit per grid step.

| Grid side | Available nodes | Obstacles | Raw A* ms | Calibrated A* ms | Raw visited | Calibrated visited | Same optimal cost |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 25 | 519 | 106 | 0.524 | 0.514 | 566 | 535 | Yes |
| 50 | 2,070 | 430 | 2.227 | 3.176 | 2,278 | 2,425 | Yes |
| 75 | 4,608 | 1,017 | 6.004 | 6.350 | 5,128 | 5,709 | Yes |

Calibration improved the smallest network by approximately 2.0% in runtime and 5.5% in node expansions. It worsened the 50-side network by approximately 42.6% in runtime and 6.5% in expansions, and worsened the 75-side network by approximately 5.8% in runtime and 11.3% in expansions. Every result preserved the Dijkstra path cost.

The conclusion is that **calibration fixed the scale mismatch but did not guarantee lower runtime**. The current implementation uses a stable queue with insertion order and a heuristic that is admissible under the benchmark’s minimum edge cost, but it does not use a closed set or decrease-key operation. Obstacle-induced detours also make straight-line distance less predictive. The next optimization should add a closed-set policy, measure stale queue pops, and test a tighter lower-bound heuristic derived from the minimum observed cost per grid step. The results should be treated as empirical behavior of this implementation, not a universal ranking of Dijkstra and A*.

## Lagged and rolling demand features

The real dataset is the UCI Bike Sharing hourly dataset, which contains 17,389 observations with weather and seasonal information [1]. The updated pipeline removes the first 168 rows without sufficient history and uses a chronological 80/20 split. It adds `demand_lag_1`, `demand_lag_24`, a prior-24-hour rolling mean, and a prior-168-hour rolling mean. Each rolling feature shifts the target before aggregation, so the current target is not included in its own features.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Seasonal mean | 174.214 | 231.076 | -0.105 |
| Gradient Boosting | 40.908 | 64.139 | 0.915 |
| Random Forest | 31.022 | 52.109 | 0.944 |
| **XGBoost with lag/rolling features** | **29.424** | **46.687** | **0.955** |

Compared with the earlier calendar/weather-only XGBoost result of MAE 43.289 and RMSE 66.985, the lagged pipeline reduces MAE by approximately 32.0% and RMSE by approximately 30.3%. This confirms that recent demand history is highly informative for this dataset. The evaluation remains a one-step-style feature construction using observed historical target values; multi-step production forecasting should recursively update lag features from predictions and should be evaluated separately.

## End-to-end ML-to-routing integration

The integration test converts a forecast into a bounded order demand value, creates a validated order, constructs a road graph, and routes the order through the A* graph-dispatch router. It verifies that the forecast-derived demand is accepted by the order model, that a route exists, that the path is correct, and that vehicle load equals the routed demand. The full suite passes with 14 tests.

## Reusable skill

The reusable skill is installed at `/home/ubuntu/skills/optima-x-research-workflow/`. It includes the workflow instructions in `SKILL.md` and a runner at `scripts/run_workflow.py`. The skill validator reports that the skill is valid. It standardizes repository auditing, real-data provenance, temporal splitting, leakage-safe feature construction, A* calibration experiments, ML-to-routing tests, artifact generation, and quality gates.

### References

[1]: https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset "Bike Sharing — UCI Machine Learning Repository"
[2]: https://doi.org/10.24432/C5W894 "Bike Sharing dataset DOI"
