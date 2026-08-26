"""Benchmark Dijkstra and A* on deterministic grid road networks."""
from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import random
from statistics import mean
from time import perf_counter
from src.dsa.graphs.astar import shortest_path as astar
from src.dsa.graphs.dijkstra import shortest_path as dijkstra
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node

def build_grid(side: int, seed: int = 42) -> RoadGraph:
    rng = random.Random(seed); graph = RoadGraph()
    for row in range(side):
        for col in range(side): graph.add_node(Node(f'{row},{col}', row / side, col / side))
    for row in range(side):
        for col in range(side):
            for dr, dc in ((1, 0), (0, 1)):
                nr, nc = row + dr, col + dc
                if nr < side and nc < side: graph.add_edge(Edge(f'{row},{col}', f'{nr},{nc}', 1.0 + rng.random() * 0.25), bidirectional=True)
    return graph

def benchmark(side: int, repetitions: int = 3) -> list[dict]:
    graph = build_grid(side); start, goal = '0,0', f'{side-1},{side-1}'; rows=[]
    for name, solver in [('dijkstra', dijkstra), ('astar', astar)]:
        samples=[]
        for _ in range(repetitions):
            began=perf_counter(); result=solver(graph, start, goal); elapsed=(perf_counter()-began)*1000
            samples.append({'runtime_ms': elapsed, 'visited_nodes': result.visited, 'path_cost': result.cost})
        rows.append({'algorithm':name, 'grid_side':side, 'nodes':side*side, 'edges':2*side*(side-1), 'runtime_ms_mean':mean(x['runtime_ms'] for x in samples), 'visited_nodes_mean':mean(x['visited_nodes'] for x in samples), 'path_cost':samples[0]['path_cost']})
    return rows

def run(sizes=(10, 25, 50, 75), repetitions=3, output='data/processed/graph_benchmark.csv'):
    rows=[row for side in sizes for row in benchmark(side, repetitions)]
    path=Path(output); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as file:
        writer=csv.DictWriter(file, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
    return rows

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--sizes', nargs='+', type=int, default=[10,25,50,75]); parser.add_argument('--repetitions', type=int, default=3); parser.add_argument('--output', default='data/processed/graph_benchmark.csv'); args=parser.parse_args()
    for row in run(args.sizes, args.repetitions, args.output): print(row)
