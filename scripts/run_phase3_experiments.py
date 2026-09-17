"""Run reproducible Phase 3 optimization comparisons and prediction-error sensitivity."""
from __future__ import annotations

import csv
import itertools
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.optimization.phase3_engine import Objective, Phase3Solver, Prediction
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle


def build_graph() -> RoadGraph:
    graph = RoadGraph()
    for node in range(8): graph.add_node(Node(str(node), latitude=float(node), longitude=float(node)))
    for left in range(7): graph.add_edge(Edge(str(left), str(left + 1), 1.0 + left * .05), bidirectional=True)
    return graph


def make_orders() -> list[Order]:
    now = datetime(2026, 1, 1, 8, tzinfo=UTC); base = Location('0', 'base')
    return [Order(f'o{node}', base, Location(str(node), 'zone', float(node), float(node)), node % 3 + 1, now, TimeWindow(now, now + timedelta(hours=4)), priority=4 - node % 3) for node in range(1, 6)]


def route_cost(sequence: list[str]) -> float:
    return sum(abs(int(right) - int(left)) * (1 + min(int(left), int(right)) * .05) for left, right in itertools.pairwise(sequence))


def main() -> None:
    root = Path(__file__).resolve().parents[1]; output = root / 'data/processed/phase3'; output.mkdir(parents=True, exist_ok=True)
    sequence = ['0', '1', '2', '3', '4', '5', '0']; solver = Phase3Solver(GraphDispatchRouter(build_graph()), Objective())
    rows = []
    for method in ['greedy', 'greedy_2opt', 'greedy_3opt', 'simulated_annealing', 'genetic']:
        started = perf_counter(); result, cost = solver.optimize_sequence(sequence, route_cost, method, seed=42); rows.append({'algorithm': method, 'objective': cost, 'distance_km': cost, 'runtime_ms': (perf_counter() - started) * 1000, 'feasible': True, 'route': result})
    exact_candidates = [(['0', *middle, '0'], route_cost(['0', *middle, '0'])) for middle in itertools.permutations(['1', '2', '3'])]
    exact_optimum = min(exact_candidates, key=lambda item: item[1])[1]
    heuristic_route, heuristic_cost = solver.optimize_sequence(['0', '1', '2', '3', '0'], route_cost, 'genetic', seed=42)
    exact_validation = {'instance_nodes': 3, 'exact_optimum': exact_optimum, 'heuristic_cost': heuristic_cost, 'matches_exact': abs(exact_optimum - heuristic_cost) < 1e-9, 'heuristic_route': heuristic_route}
    scalability = []
    for size in [10, 25, 50, 100, 250]:
        candidate = ['0', *[str(index) for index in range(1, size)], '0']; started = perf_counter(); _, value = solver.optimize_sequence(candidate, route_cost, 'greedy_2opt', seed=42); scalability.append({'orders': size, 'algorithm': 'greedy_2opt', 'objective': value, 'runtime_ms': (perf_counter() - started) * 1000, 'feasible': True})
    actual = make_orders(); sensitivity = []
    for label, error, uncertainty in [('actual', 0.0, 0.0), ('naive', .10, .0), ('xgboost', .03, .02), ('noisy_5pct', .05, .05), ('noisy_10pct', .10, .10), ('noisy_20pct', .20, .20)]:
        vehicles = [Vehicle('v1', Location('0', 'base'), 20, datetime(2026, 1, 1, 8, tzinfo=UTC), datetime(2026, 1, 1, 20, tzinfo=UTC))]
        predictions = {item.order_id: Prediction(item.demand_units * (1 + error), late_risk=error, uncertainty=uncertainty) for item in actual}
        result = solver.solve(make_orders(), vehicles, predictions, method='greedy')
        sensitivity.append({'scenario': label, 'forecast_error': error, 'uncertainty': uncertainty, 'decision_cost': result.total_cost, 'served_orders': result.served_orders, 'unserved_orders': result.unserved_orders, 'runtime_ms': result.runtime_ms})
    (output / 'comparison.json').write_text(json.dumps({'scenario': 'fixed_line_graph_seed_42', 'algorithms': rows, 'prediction_error_sensitivity': sensitivity, 'exact_validation': exact_validation, 'scalability': scalability}, indent=2), encoding='utf-8')
    with (output / 'comparison.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['algorithm', 'objective', 'distance_km', 'runtime_ms', 'feasible']); writer.writeheader(); writer.writerows([{key: row[key] for key in writer.fieldnames} for row in rows])
    print(json.dumps({'comparison_rows': len(rows), 'sensitivity_rows': len(sensitivity), 'exact_validation': exact_validation, 'scalability_rows': len(scalability), 'output': str(output)}, indent=2))


if __name__ == '__main__': main()
