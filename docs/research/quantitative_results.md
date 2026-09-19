# Quantitative Results Register

**Author: Karthikeya**

This register records the headline numbers currently safe to present on the OPTIMA-X repository landing page. They are copied from the reproducible benchmark report rather than estimated from implementation status.

| Experiment | Dataset and split | Result | Interpretation |
|---|---|---|---|
| Demand forecasting | UCI Bike Sharing, chronological 80/20 split, 17,389 observations | XGBoost MAE 43.289, RMSE 66.985, R² 0.908 | Best of the listed tabular models |
| Baseline comparison | Same split | Seasonal mean MAE 174.985, RMSE 232.608, R² -0.113 | XGBoost improves MAE by 75.3% and RMSE by 71.2% |
| Graph search | Deterministic weighted square grids, 10–100 side length | Same final path cost for Dijkstra and A* | Correctness parity holds across tested scales |
| Graph runtime | Same graph benchmark | A* runtime ratio 1.33–1.50× Dijkstra | Current coordinate heuristic is not calibrated to edge-cost units |
| Graph expansion | Same graph benchmark | A* visits 1.16–1.23× Dijkstra nodes | The result is an implementation diagnostic, not a universal algorithm ranking |

The full methodology, model table, caveats, and references are in [`benchmark_and_forecasting_report.md`](benchmark_and_forecasting_report.md). Future claims should add the exact artifact path and preserve the chronological split; random shuffling would make the time-series comparison less credible.
