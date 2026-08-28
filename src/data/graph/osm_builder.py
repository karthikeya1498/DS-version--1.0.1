"""Build a RoadGraph from an OpenStreetMap XML extract.

The importer intentionally accepts a local extract so experiments remain reproducible.
Use an external downloader separately and record its source manifest.
"""
from __future__ import annotations

from itertools import pairwise
from pathlib import Path

from defusedxml import ElementTree

from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node

_ALLOWED_HIGHWAYS = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'service'}

def build_from_osm_xml(path: str | Path) -> RoadGraph:
    root = ElementTree.parse(path).getroot()
    coordinates = {element.attrib['id']: (float(element.attrib['lat']), float(element.attrib['lon'])) for element in root.findall('node')}
    graph = RoadGraph()
    for node_id, (latitude, longitude) in coordinates.items(): graph.add_node(Node(node_id, latitude, longitude))
    for way in root.findall('way'):
        tags = {tag.attrib.get('k'): tag.attrib.get('v') for tag in way.findall('tag')}
        if tags.get('highway') not in _ALLOWED_HIGHWAYS: continue
        refs = [node.attrib['ref'] for node in way.findall('nd')]
        for source, target in pairwise(refs):
            if source not in graph.nodes or target not in graph.nodes: continue
            a, b = graph.nodes[source], graph.nodes[target]
            distance = ((a.latitude - b.latitude) ** 2 + (a.longitude - b.longitude) ** 2) ** .5
            graph.add_edge(Edge(source, target, max(distance, 1e-9)), bidirectional=tags.get('oneway') != 'yes')
    return graph
