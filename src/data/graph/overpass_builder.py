"""Build a RoadGraph from Overpass JSON geometry responses."""
from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node


def build_from_overpass_json(path: str | Path) -> RoadGraph:
    payload = json.loads(Path(path).read_text(encoding='utf-8')); graph = RoadGraph(); seen = {}
    for element in payload.get('elements', []):
        geometry = element.get('geometry', [])
        refs = [str(point.get('lat')) + ':' + str(point.get('lon')) for point in geometry]
        for point in geometry:
            node_id = str(point.get('lat')) + ':' + str(point.get('lon')); seen[node_id] = (float(point['lat']), float(point['lon']))
    for node_id, (latitude, longitude) in seen.items(): graph.add_node(Node(node_id, latitude, longitude))
    for element in payload.get('elements', []):
        raw_tags = element.get('tags', {}); tags = raw_tags if isinstance(raw_tags, dict) else {tag.get('k'): tag.get('v') for tag in raw_tags}; geometry = element.get('geometry', [])
        if tags.get('highway') is None: continue
        refs = [str(point.get('lat')) + ':' + str(point.get('lon')) for point in geometry]
        for source, target in pairwise(refs):
            a, b = graph.nodes[source], graph.nodes[target]; distance = ((a.latitude-b.latitude)**2 + (a.longitude-b.longitude)**2)**.5
            graph.add_edge(Edge(source, target, max(distance, 1e-9)), bidirectional=tags.get('oneway') != 'yes')
    return graph
