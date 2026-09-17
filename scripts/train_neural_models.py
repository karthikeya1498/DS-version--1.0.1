"""Train and evaluate MLP and temporal neural demand models.

Author: Karthikeya
The script extends the existing chronological Phase 2 benchmark without
replacing XGBoost. It writes comparable MAE, RMSE, and R2 metrics with model
metadata and preserves the no-future-leakage feature construction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from scripts.train_models import FEATURES, load_hourly
except ModuleNotFoundError:  # Direct execution places the scripts directory on sys.path.
    from train_models import FEATURES, load_hourly
from src.ml.demand.neural_models import MLPDemandForecaster, TemporalDemandForecaster


def _metrics(actual: np.ndarray, predicted: list[float]) -> dict[str, float]:
    values = np.asarray(predicted, dtype=float)
    return {"mae": float(mean_absolute_error(actual, values)), "rmse": float(mean_squared_error(actual, values) ** 0.5), "r2": float(r2_score(actual, values))}


def _sequence_data(features: np.ndarray, target: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    if len(features) <= window:
        raise ValueError("dataset must contain more rows than the sequence window")
    sequences = np.stack([features[index - window:index] for index in range(window, len(features))])
    return sequences, target[window:]


def evaluate(data: str | Path, output: str | Path, epochs: int = 40, window: int = 24, cell: str = "lstm") -> dict[str, object]:
    frame = load_hourly(data)
    split = int(len(frame) * 0.8)
    features = frame[FEATURES].to_numpy(dtype=np.float32)
    target = frame["cnt"].to_numpy(dtype=np.float32)
    mlp = MLPDemandForecaster(epochs=epochs, random_state=42).fit(features[:split], target[:split])
    mlp_predictions = mlp.predict(features[split:])
    sequence_features, sequence_target = _sequence_data(features, target, window)
    sequence_split = max(1, int(len(sequence_features) * 0.8))
    temporal = TemporalDemandForecaster(cell=cell, epochs=epochs, random_state=42).fit(sequence_features[:sequence_split], sequence_target[:sequence_split])
    temporal_predictions = temporal.predict(sequence_features[sequence_split:])
    results: dict[str, object] = {
        "dataset": "UCI Bike Sharing hourly",
        "features": FEATURES,
        "window": window,
        "split": {"mlp_train": split, "mlp_test": len(features) - split, "temporal_train": sequence_split, "temporal_test": len(sequence_features) - sequence_split},
        "models": {"mlp": {**_metrics(target[split:], mlp_predictions), "metadata": mlp.metadata()}, cell: {**_metrics(sequence_target[sequence_split:], temporal_predictions), "metadata": temporal.metadata()}},
    }
    target_path = Path(output)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/raw/mobility/hour.csv")
    parser.add_argument("--output", default="data/processed/neural_forecast_metrics.json")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--window", type=int, default=24)
    parser.add_argument("--cell", choices=("lstm", "gru"), default="lstm")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.data, args.output, args.epochs, args.window, args.cell), indent=2))


if __name__ == "__main__":
    main()
