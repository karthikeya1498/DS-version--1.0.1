# Benchmark and Forecasting Analysis

## Executive summary

The benchmark compares the current Python implementations of Dijkstra and A* on deterministic weighted square-grid road networks. Both algorithms returned identical path costs at every tested scale. In this implementation and workload, A* was slower and expanded more nodes than Dijkstra because the coordinate heuristic is not calibrated to the edge-cost scale: geographic coordinate differences are below one while edge weights are approximately one to 1.25. Consequently, the heuristic contributes little useful ordering information and adds computation overhead.

The ML pipeline uses the **UCI Bike Sharing hourly dataset**, which contains 17,389 hourly and daily observations from the Capital Bikeshare system with weather and seasonal information [1]. A chronological 80/20 split was used to avoid future-to-past leakage. XGBoost produced the best result among the evaluated models, with MAE 43.29, RMSE 66.99, and R² 0.908.

## Graph benchmark

Each network is a square grid with bidirectional edges and deterministic random weights in the range 1.00–1.25. The benchmark performs five repetitions for each size and records mean runtime, mean expanded nodes, and final path cost.

| Grid side | Nodes | Dijkstra ms | A* ms | A*/Dijkstra runtime | Dijkstra visited | A* visited | A*/Dijkstra visited | Same cost |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 10 | 100 | 0.077 | 0.106 | 1.38x | 100 | 116 | 1.16x | Yes |
| 25 | 625 | 0.516 | 0.714 | 1.38x | 625 | 767 | 1.23x | Yes |
| 50 | 2,500 | 2.122 | 3.103 | 1.46x | 2,500 | 3,013 | 1.21x | Yes |
| 75 | 5,625 | 5.601 | 7.432 | 1.33x | 5,625 | 6,746 | 1.20x | Yes |
| 100 | 10,000 | 11.584 | 17.412 | 1.50x | 10,000 | 12,039 | 1.20x | Yes |

Runtime grows approximately linearly with the number of grid nodes in this range. Dijkstra expands every node because the benchmark’s goal is at the far corner and the graph has many equal or near-equal frontier alternatives. A* does not improve the result because its heuristic is too small relative to the edge costs. This is an implementation diagnostic rather than evidence that A* is universally inferior.

For a fairer A* experiment, edge weights should be derived from physical distance in the same units as the heuristic, or the heuristic should be multiplied by a lower-bound cost-per-coordinate-unit. A larger irregular road graph, obstacles, and a calibrated admissible heuristic would better expose A*’s intended advantage.

## Forecasting pipeline

The training script is `scripts/train_models.py`. It loads `data/raw/mobility/hour.csv`, constructs a timestamp, selects calendar, weather, and normalized-condition features, performs a chronological split, trains a seasonal-mean baseline, Gradient Boosting, Random Forest, and native XGBoost when installed, and writes metrics to `data/processed/forecast_metrics.json`.

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Seasonal mean baseline | 174.985 | 232.608 | -0.113 |
| Gradient Boosting | 73.617 | 107.438 | 0.763 |
| Random Forest | 45.622 | 70.261 | 0.898 |
| XGBoost | **43.289** | **66.985** | **0.908** |

Relative to the seasonal baseline, XGBoost reduces MAE by approximately 75.3% and RMSE by approximately 71.2%. The comparison is useful as a strong tabular baseline, but it should not yet be interpreted as a deployment-quality forecast: the current feature set does not include lagged demand, rolling statistics, explicit weather interactions, or prediction intervals.

## Reproducibility artifacts

The raw dataset is stored under `data/raw/mobility/`. The benchmark CSV is `data/processed/graph_benchmark.csv`. The derived benchmark analysis is `data/processed/benchmark_analysis.json`, and the forecasting metrics are `data/processed/forecast_metrics.json`. Charts are stored as `data/processed/graph_benchmark.png` and `data/processed/forecast_mae.png`.

### References

[1]: https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset "Bike Sharing — UCI Machine Learning Repository"
[2]: https://doi.org/10.24432/C5W894 "Bike Sharing dataset DOI"
