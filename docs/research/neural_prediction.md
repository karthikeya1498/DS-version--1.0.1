# OPTIMA-X Neural Prediction Layer

**Author:** Karthikeya  
**Phase:** 2 — ML Prediction  
**Downstream consumer:** Phase 3 constrained optimization

## Design decision

The neural models are implemented as controlled peers to the existing baseline and XGBoost path. They do not replace XGBoost and are not presented as automatically superior. The research question is whether a neural architecture improves prediction metrics and, more importantly, whether that improvement produces better downstream operational decisions.

| Model | Data shape | Intended use |
|---|---|---|
| Seasonal baseline | One-dimensional history | Sanity-check reference. |
| XGBoost | Tabular leakage-safe features | Strong tabular baseline. |
| MLP | Two-dimensional tabular feature matrix | Neural nonlinear baseline for demand. |
| LSTM | Three-dimensional sequence windows | Temporal demand dependencies. |
| GRU | Three-dimensional sequence windows | Lower-complexity temporal comparison. |

## Implemented interfaces

`MLPDemandForecaster` accepts an `N × F` numeric matrix and an `N` target vector. It standardizes features and targets using training-only statistics, trains a small fully connected ReLU network with deterministic PyTorch seeding, and returns predictions in the original target scale.

`TemporalDemandForecaster` accepts an `N × W × F` sequence tensor, where `W` is a historical window such as 24 hours. It supports `cell="lstm"` and `cell="gru"`, uses the final recurrent state for the next target, and applies the same training-only standardization discipline.

Both models expose metadata containing architecture, learning rate, epoch count, random seed, and final loss. The MLP also supports saving a state dictionary and normalization statistics for registry integration.

## Reproducible training

```bash
python scripts/train_neural_models.py \
  --data data/raw/mobility/hour.csv \
  --output data/processed/neural_forecast_metrics.json \
  --epochs 40 \
  --window 24 \
  --cell lstm
```

The script reuses the existing chronological `load_hourly` feature construction. Lag and rolling features are shifted before calculation, and the train/test split remains chronological. The MLP uses the original tabular split. The temporal model builds sequence windows and applies a second chronological split after window construction.

## Phase 3 integration contract

Neural demand predictions remain ordinary numerical outputs and can populate the existing `Prediction` contract:

```python
Prediction(
    demand=neural_demand,
    eta_minutes=baseline_eta,
    late_risk=late_risk_model_output,
    uncertainty=validation_error_estimate,
)
```

The optimizer therefore remains model-agnostic. It receives demand, ETA, late-risk, and uncertainty fields and ranks assignments under the same constraints and objective weights regardless of whether demand came from a baseline, XGBoost, MLP, LSTM, or GRU.

## Evaluation protocol

Compare baseline, XGBoost, MLP, LSTM, and GRU using the same final test period. Report MAE, RMSE, and R² for prediction, then feed each prediction set into Phase 3 and report lateness, unserved orders, distance, total cost, feasibility, and runtime. Do not tune on the final test period. For stochastic neural training, retain multiple seeds and report central tendency and spread.

The current repository has no implemented graph-tensor pipeline with node-level labels, so a GNN is intentionally not fabricated. A future GNN revision should first define graph snapshots, edge/node features, temporal alignment, and a leakage-safe graph split before claiming graph-model results.

## Limitations

The neural layer requires the optional PyTorch dependency and CPU-friendly defaults. The models are research baselines, not production-calibrated predictors. They do not automatically provide uncertainty estimates; the existing `uncertainty` field must be populated by a separate validation or ensemble procedure. Training artifacts should be registered with dataset, feature, environment, and code versions before production use.
