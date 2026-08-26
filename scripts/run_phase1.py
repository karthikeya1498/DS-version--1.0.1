"""Run Phase 1 acceptance checks and write a compact status artifact."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.preprocess import process
from scripts.run_simulation import run


def main() -> dict:
    root = Path(__file__).resolve().parents[1]
    manifest = process(root / 'data/raw/mobility/hour.csv', root / 'data/processed/mobility_hour_clean.csv')
    simulation = run(seed=42, duration_hours=8, zones=5, vehicles=10, orders_per_hour=20)
    status = {'scenario': simulation['scenario_id'], 'nodes': simulation['nodes'], 'edges': simulation['edges'], 'vehicles': simulation['vehicles'], 'orders': simulation['orders'], 'traffic_state': simulation['traffic_state'], 'demand_multiplier': simulation['demand_multiplier'], 'graph_built': simulation['graph_built'], 'data_validated': manifest['validated'], 'simulation': simulation['simulation'], 'source_rows': manifest['rows']}
    output = root / 'data/processed/phase1_status.json'; output.write_text(json.dumps(status, indent=2), encoding='utf-8'); print(json.dumps(status, indent=2)); return status

if __name__ == '__main__': main()
