"""Build a graph summary from the downloaded Overpass road extract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.graph.overpass_builder import build_from_overpass_json


def build(input_path: str | Path = 'data/raw/osm/manhattan_roads.json', output_path: str | Path = 'data/processed/osm_graph_summary.json') -> dict:
    graph = build_from_overpass_json(input_path); summary = {'source': str(input_path), 'nodes': len(graph.nodes), 'directed_edges': sum(len(edges) for edges in graph.adjacency.values()), 'graph_built': True}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True); Path(output_path).write_text(json.dumps(summary, indent=2), encoding='utf-8'); return summary

if __name__ == '__main__': print(json.dumps(build(), indent=2))
