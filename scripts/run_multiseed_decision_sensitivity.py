"""Run paired multi-seed decision-cost sensitivity experiments.

Author: Karthikeya
The benchmark keeps data, orders, optimizer, objective weights, and seed sets
explicit while varying fleet capacity, route-cost alternatives, and controlled
prediction treatments. It reports per-run and aggregate operational outcomes.
"""
from __future__ import annotations

import argparse
import json
import statistics
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

SEEDS = (7, 42, 99, 123, 2026)
CAPACITIES = (5, 10, 20)
ROUTE_PROFILES = ("balanced", "north_bias", "south_bias")
TREATMENTS = ("clean", "noise_10pct", "priority_targeted")


def build_graph(profile: str) -> RoadGraph:
    if profile not in ROUTE_PROFILES:
        raise ValueError(f"unsupported route profile: {profile}")
    graph = RoadGraph()
    for node in range(8):
        graph.add_node(Node(str(node), latitude=float(node), longitude=float(node)))
    for left in range(7):
        multiplier = 1.0
        if profile == "north_bias":
            multiplier = 0.75 if left >= 4 else 1.25
        elif profile == "south_bias":
            multiplier = 1.25 if left >= 4 else 0.75
        graph.add_edge(Edge(str(left), str(left + 1), (1.0 + left * 0.05) * multiplier), bidirectional=True)
    return graph


def make_orders(actual: np.ndarray) -> list[Order]:
    now = datetime(2026, 1, 1, 8, tzinfo=UTC)
    base = Location("0", "base")
    return [
        Order(f"o{node}", base, Location(str(node), "zone", float(node), float(node)), max(1, round(float(actual[node - 1])) % 4 + 1), now, TimeWindow(now, now + timedelta(hours=4)), priority=5 - node % 3)
        for node in range(1, 6)
    ]


def model_predictions(frame, seed: int, epochs: int, window: int) -> tuple[dict[str, np.ndarray], np.ndarray]:
    features = frame[FEATURES].to_numpy(dtype=np.float32)
    target = frame["cnt"].to_numpy(dtype=np.float32)
    split = int(len(frame) * 0.8)
    x_test = features[split : split + 5]
    models: dict[str, np.ndarray] = {}
    xgboost = DemandForecaster(random_state=seed, n_estimators=200).fit(features[:split], target[:split])
    models["xgboost"] = np.asarray(xgboost.predict(x_test), dtype=float)
    mlp = MLPDemandForecaster(epochs=epochs, random_state=seed).fit(features[:split], target[:split])
    models["mlp"] = np.asarray(mlp.predict(x_test), dtype=float)
    sequence_features = np.stack([features[index - window : index] for index in range(window, len(features))])
    sequence_target = target[window:]
    sequence_split = max(1, int(len(sequence_features) * 0.8))
    temporal = TemporalDemandForecaster(cell="lstm", epochs=epochs, random_state=seed).fit(sequence_features[:sequence_split], sequence_target[:sequence_split])
    models["lstm"] = np.asarray(temporal.predict(sequence_features[sequence_split : sequence_split + 5]), dtype=float)
    return models, sequence_target[sequence_split : sequence_split + 5]


def treated_predictions(predictions: np.ndarray, actual: np.ndarray, treatment: str, seed: int) -> np.ndarray:
    if treatment == "clean":
        return predictions.copy()
    if treatment == "noise_10pct":
        rng = np.random.default_rng(seed)
        return predictions * (1.0 + rng.normal(0.0, 0.10, size=len(predictions)))
    if treatment == "priority_targeted":
        result = predictions.copy()
        result[0] += actual[0] * 0.20
        return result
    raise ValueError(f"unsupported treatment: {treatment}")


def decision_metrics(actual: np.ndarray, predictions: np.ndarray, capacity: int, route_profile: str) -> dict[str, float | int | bool]:
    shift_start = datetime(2026, 1, 1, 8, tzinfo=UTC)
    orders = make_orders(actual)
    vehicles = [Vehicle(f"v{index}", Location(str(index * 7), f"base-{index}"), capacity, shift_start, shift_start + timedelta(hours=12)) for index in range(2)]
    solver = Phase3Solver(GraphDispatchRouter(build_graph(route_profile)), Objective())
    mapped = {order.order_id: Prediction(float(predictions[index]), late_risk=float(max(0.0, predictions[index] - actual[index]) / max(actual[index], 1.0)), uncertainty=float(abs(predictions[index] - actual[index]) / max(actual[index], 1.0))) for index, order in enumerate(orders)}
    result = solver.solve(orders, vehicles, mapped, method="greedy")
    return {"decision_cost": result.total_cost, "distance_km": sum(route.distance_km for route in result.routes), "lateness_minutes": sum(route.lateness_minutes for route in result.routes), "served_orders": result.served_orders, "unserved_orders": result.unserved_orders, "feasible": all(route.feasible for route in result.routes), "optimization_runtime_ms": result.runtime_ms}


def run(data: str | Path, output: str | Path, epochs: int = 12, window: int = 24) -> dict[str, object]:
    frame = load_hourly(data)
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        model_outputs, actual = model_predictions(frame, seed, epochs, window)
        for model, predictions in model_outputs.items():
            for treatment in TREATMENTS:
                treated = treated_predictions(predictions, actual, treatment, seed)
                for capacity in CAPACITIES:
                    for route_profile in ROUTE_PROFILES:
                        rows.append({"seed": seed, "model": model, "treatment": treatment, "capacity": capacity, "route_profile": route_profile, "prediction_mae": float(mean_absolute_error(actual, treated)), "prediction_rmse": float(mean_squared_error(actual, treated) ** 0.5), **decision_metrics(actual, treated, capacity, route_profile)})
    groups: dict[tuple[str, str, int, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (str(row["model"]), str(row["treatment"]), int(row["capacity"]), str(row["route_profile"]))
        groups.setdefault(key, []).append(row)
    aggregates = []
    for (model, treatment, capacity, route_profile), values in groups.items():
        costs = [float(value["decision_cost"]) for value in values]
        aggregates.append({"model": model, "treatment": treatment, "capacity": capacity, "route_profile": route_profile, "seeds": len(values), "mean_decision_cost": statistics.fmean(costs), "std_decision_cost": statistics.pstdev(costs), "min_decision_cost": min(costs), "max_decision_cost": max(costs), "mean_lateness_minutes": statistics.fmean(float(value["lateness_minutes"]) for value in values), "mean_unserved_orders": statistics.fmean(float(value["unserved_orders"]) for value in values), "mean_served_orders": statistics.fmean(float(value["served_orders"]) for value in values)})
    result = {"research_question": "How stable is downstream decision cost across model seeds, fleet capacities, route-cost alternatives, and prediction error treatments?", "seeds": SEEDS, "capacities": CAPACITIES, "route_profiles": ROUTE_PROFILES, "treatments": TREATMENTS, "fixed_optimizer": "Phase3Solver/greedy/A*", "rows": rows, "aggregates": aggregates}
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/raw/mobility/hour.csv")
    parser.add_argument("--output", default="data/processed/phase7_multiseed_sensitivity.json")
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--window", type=int, default=24)
    args = parser.parse_args()
    print(json.dumps(run(args.data, args.output, args.epochs, args.window), indent=2))


if __name__ == "__main__":
    main()
