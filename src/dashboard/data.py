"""Dashboard data accessors kept separate from Streamlit rendering."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import pandas as pd


def load_osm_edges(root: str | Path, limit: int = 2500) -> pd.DataFrame:
    path = Path(root) / "data/raw/osm/manhattan_roads.json"
    if not path.exists():
        return pd.DataFrame(columns=["x0", "y0", "x1", "y1"])
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in payload.get("elements", []):
        geometry = item.get("geometry", []) if item.get("type") == "way" else []
        for start, end in itertools.pairwise(geometry):
            if None not in (start.get("lon"), start.get("lat"), end.get("lon"), end.get("lat")):
                rows.append(
                    {"x0": start["lon"], "y0": start["lat"], "x1": end["lon"], "y1": end["lat"]}
                )
            if len(rows) >= limit:
                return pd.DataFrame(rows)
    return pd.DataFrame(rows)


def load_json(path: str | Path, default: dict | None = None) -> dict:
    file = Path(path)
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else (default or {})


def load_forecast_metrics(root: str | Path) -> pd.DataFrame:
    path = Path(root) / "data/processed/unified_demand_metrics.json"
    if not path.exists():
        path = Path(root) / "data/processed/forecast_metrics_lagged.json"
    payload = load_json(path, {})
    models = payload.get("models")
    if models:
        return pd.DataFrame(models).T.reset_index(names="model")
    metrics = payload.get("metrics", {})
    return (
        pd.DataFrame([{"model": payload.get("dataset", "forecast"), **metrics}])
        if metrics
        else pd.DataFrame()
    )


def load_phase3_comparison(root: str | Path) -> pd.DataFrame:
    path = Path(root) / "data/processed/phase3/comparison.json"
    payload = load_json(path, {})
    return pd.DataFrame(payload.get("algorithms", []))


def load_phase3_sensitivity(root: str | Path) -> pd.DataFrame:
    path = Path(root) / "data/processed/phase3/comparison.json"
    payload = load_json(path, {})
    return pd.DataFrame(payload.get("prediction_error_sensitivity", []))


def load_rl_evaluation(root: str | Path) -> dict:
    return load_json(Path(root) / "data/processed/phase4/evaluation.json", {})


def load_benchmark(root: str | Path) -> pd.DataFrame:
    path = Path(root) / "data/processed/graph_benchmark.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_phase1_status(root: str | Path) -> dict:
    return load_json(Path(root) / "data/processed/phase1_status.json", {})


def dispatch_rows(simulation_summary: dict) -> pd.DataFrame:
    metrics = simulation_summary.get("metrics", {})
    return pd.DataFrame(
        [
            {"metric": key.replace("_", " ").title(), "value": value}
            for key, value in metrics.items()
        ]
    )


def vehicle_dispatch_rows(simulation_summary: dict) -> pd.DataFrame:
    return pd.DataFrame(simulation_summary.get("vehicle_dispatches", []))
