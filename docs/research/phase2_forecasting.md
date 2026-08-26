# Phase 2: Feature Engineering and Demand Forecasting

Phase 2 converts the operational data produced in Phase 1 into predictive demand intelligence. The feature pipeline is reusable and lives outside notebooks so that training, evaluation, API inference, and future decision experiments share one definition.

## Forecast target

For an observation at time $t$, the current implementation predicts next-period demand:

$$y(t+1)=Demand_{t+1}$$

using only features available at or before $t$. The implementation sorts by timestamp, groups by zone when available, shifts demand before calculating rolling features, and removes rows without complete history.

## Features

| Family | Features |
|---|---|
| Calendar | hour, day of week, day of month, weekend |
| Lagged demand | lag 1, lag 2, lag 24 |
| Rolling demand | prior 3, 6, and 24-period means |
| Target | next-period demand |

The chronological split is deterministic and separates training, optional validation, and test partitions without random shuffling.

## Model contract

`DemandForecaster` uses native XGBoost when installed and falls back to a deterministic mean model when the optional dependency is unavailable. The model exposes `fit`, `predict`, and `metadata`, making the same contract usable by scripts and API adapters.

The real UCI Bike Sharing hourly data currently produces 17,354 usable rows after lag and target trimming. A seeded run uses 13,883 training rows and 3,471 test rows. The generated metrics artifact records the dataset path, feature names, model type, random seed, and MAE/RMSE/SMAPE.

## Phase 2 acceptance criteria

Phase 2 is accepted when feature generation is leakage-safe, chronological splitting is tested, the XGBoost-compatible model trains on the real dataset, metrics are persisted, and the existing simulation/routing tests remain green. The next decision experiment will compare current-demand and predicted-demand order allocation under the same seeded scenarios.
