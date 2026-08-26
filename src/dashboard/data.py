"""Dashboard data accessors kept separate from Streamlit rendering."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_json(path: str | Path, default: dict | None = None) -> dict:
    file = Path(path)
    return json.loads(file.read_text(encoding='utf-8')) if file.exists() else (default or {})

def load_forecast_metrics(root: str | Path) -> pd.DataFrame:
    payload = load_json(Path(root) / 'data/processed/forecast_metrics_lagged.json', {})
    models = payload.get('models', payload.get('metrics', {})); return pd.DataFrame(models).T.reset_index(names='model') if models else pd.DataFrame()

def load_benchmark(root: str | Path) -> pd.DataFrame:
    path = Path(root) / 'data/processed/graph_benchmark.csv'; return pd.read_csv(path) if path.exists() else pd.DataFrame()

def load_phase1_status(root: str | Path) -> dict: return load_json(Path(root) / 'data/processed/phase1_status.json', {})

def dispatch_rows(simulation_summary: dict) -> pd.DataFrame:
    metrics = simulation_summary.get('metrics', {}); return pd.DataFrame([{'metric': key.replace('_', ' ').title(), 'value': value} for key, value in metrics.items()])

def vehicle_dispatch_rows(simulation_summary: dict) -> pd.DataFrame:
    return pd.DataFrame(simulation_summary.get('vehicle_dispatches', []))
