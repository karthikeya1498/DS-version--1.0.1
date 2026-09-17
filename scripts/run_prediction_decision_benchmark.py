"""Run the Phase 7 prediction-to-decision propagation benchmark.

Author: Karthikeya
Every model is evaluated on the same chronological test period and every
prediction treatment is passed through the same fixed Phase 3 optimizer.
Results distinguish prediction metrics from downstream operational metrics.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.ml.demand.neural_models import MLPDemandForecaster, TemporalDemandForecaster
from src.ml.demand.xgboost_model import DemandForecaster
from src.optimization.phase3_engine import Objective, Phase3Solver, Prediction
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle

try:
    from scripts.train_models import FEATURES, load_hourly
except ModuleNotFoundError:  # Direct execution places the scripts directory on sys.path.
    from train_models import FEATURES, load_hourly


def build_graph() -> RoadGraph:
    graph = RoadGraph()
    for node in range(8):
        graph.add_node(Node(str(node), latitude=float(node), longitude=float(node)))
    for left in range(7):
        graph.add_edge(Edge(str(left), str(left + 1), 1.0 + left * 0.05), bidirectional=True)
    return graph


def make_orders(actual: np.ndarray) -> list[Order]:
    now = datetime(2026, 1, 1, 8, tzinfo=UTC)
    base = Location("0", "base")
    return [
        Order(f"o{node}", base, Location(str(node), "zone", float(node), float(node)), max(1, round(float(actual[node - 1])) % 4 + 1), now, TimeWindow(now, now + timedelta(hours=4)), priority=5 - node % 3)
        for node in range(1, 6)
    ]


def model_predictions(frame, epochs: int, window: int) -> tuple[dict[str, np.ndarray], np.ndarray]:
    features = frame[FEATURES].to_numpy(dtype=np.float32)
    target = frame["cnt"].to_numpy(dtype=np.float32)
    split = int(len(frame) * 0.8)
    mlp = MLPDemandForecaster(epochs=epochs, random_state=42).fit(features[:split], target[:split])
    predictions = {"xgboost": np.asarray(DemandForecaster(random_state=42, n_estimators=200).fit(features[:split], target[:split]).predict(features[split:5 + split]), dtype=float), "mlp": np.asarray(mlp.predict(features[split:5 + split]), dtype=float)}
    sequence_features = np.stack([features[index - window:index] for index in range(window, len(features))])
    sequence_target = target[window:]
    sequence_split = max(1, int(len(sequence_features) * 0.8))
    temporal = TemporalDemandForecaster(cell="lstm", epochs=epochs, random_state=42).fit(sequence_features[:sequence_split], sequence_target[:sequence_split])
    predictions["lstm"] = np.asarray(temporal.predict(sequence_features[sequence_split:sequence_split + 5]), dtype=float)
    actual = sequence_target[sequence_split:sequence_split + 5]
    return predictions, actual


def treatments(name: str, predictions: np.ndarray, actual: np.ndarray) -> list[tuple[str, np.ndarray]]:
    return [("clean", predictions), ("noise_5pct", predictions * 1.05), ("noise_10pct", predictions * 1.10), ("noise_20pct", predictions * 1.20), ("priority_targeted", predictions + np.where(np.arange(len(predictions)) == 0, actual * 0.20, 0.0))]


def decision_metrics(predictions: np.ndarray, actual: np.ndarray) -> dict[str, float | int | bool]:
    orders = make_orders(actual)
    shift_start = datetime(2026, 1, 1, 8, tzinfo=UTC)
    shift_end = datetime(2026, 1, 1, 20, tzinfo=UTC)
    vehicles = [
        Vehicle("v1", Location("0", "base-a"), 10, shift_start, shift_end),
        Vehicle("v2", Location("7", "base-b"), 10, shift_start, shift_end),
    ]
    solver = Phase3Solver(GraphDispatchRouter(build_graph()), Objective())
    mapped = {order.order_id: Prediction(float(predictions[index]), late_risk=float(max(0.0, predictions[index] - actual[index]) / max(actual[index], 1.0)), uncertainty=float(abs(predictions[index] - actual[index]) / max(actual[index], 1.0))) for index, order in enumerate(orders)}
    result = solver.solve(orders, vehicles, mapped, method="greedy")
    return {"decision_cost": result.total_cost, "distance_km": sum(route.distance_km for route in result.routes), "lateness_minutes": sum(route.lateness_minutes for route in result.routes), "served_orders": result.served_orders, "unserved_orders": result.unserved_orders, "feasible": all(route.feasible for route in result.routes), "optimization_runtime_ms": result.runtime_ms}


def run(data: str | Path, output: str | Path, epochs: int = 20, window: int = 24) -> dict[str, object]:
    frame = load_hourly(data)
    model_outputs, actual = model_predictions(frame, epochs, window)
    rows: list[dict[str, object]] = []
    for model, predictions in model_outputs.items():
        for treatment, treated in treatments(model, predictions, actual):
            rows.append({"model": model, "treatment": treatment, "prediction_mae": float(mean_absolute_error(actual, treated)), "prediction_rmse": float(mean_squared_error(actual, treated) ** 0.5), **decision_metrics(treated, actual)})
    result = {"research_question": "Does better predictive accuracy necessarily produce better downstream logistics decisions?", "dataset": "UCI Bike Sharing hourly", "fixed_optimizer": "Phase3Solver/greedy/A*", "seed": 42, "rows": rows}
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/raw/mobility/hour.csv")
    parser.add_argument("--output", default="data/processed/phase7_prediction_decision.json")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--window", type=int, default=24)
    args = parser.parse_args()
    print(json.dumps(run(args.data, args.output, args.epochs, args.window), indent=2))


if __name__ == "__main__":
    main()
