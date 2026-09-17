"""End-to-end smoke test for forecast, routing, dashboard, and REST service contracts."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from api.main import app
from scripts.run_simulation import run
from src.dashboard.data import vehicle_dispatch_rows
from src.dsa.graphs.edge import Edge
from src.dsa.graphs.graph import RoadGraph
from src.dsa.graphs.node import Node
from src.ml.demand.baseline import SeasonalMean
from src.optimization.routing.graph_dispatch import GraphDispatchRouter
from src.simulation.models import Location, Order, TimeWindow, Vehicle


def main() -> dict:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    forecast = SeasonalMean().fit([4, 6, 8]).predict(1)[0]
    origin = Location('a', 'zone-a', 0, 0); destination = Location('b', 'zone-b', 0, 1)
    graph = RoadGraph(); graph.add_node(Node('a', 0, 0)); graph.add_node(Node('b', 0, 1)); graph.add_edge(Edge('a', 'b', 1.0))
    vehicle = Vehicle('v1', origin, 10, now, now + timedelta(hours=2)); order = Order('o1', origin, destination, round(forecast), now, TimeWindow(now, now + timedelta(hours=1)))
    route = GraphDispatchRouter(graph, 'astar').route(order, [vehicle], now)
    snapshot = run(seed=42, duration_hours=1, vehicles=2, orders_per_hour=2)
    assert not vehicle_dispatch_rows(snapshot).empty
    client = TestClient(app); health = client.get('/api/v1/health'); token = client.post('/api/v1/auth/token', json={'username': 'system-test', 'password': 'test', 'tenant_id': 'tenant-test'}).json()['access_token']; headers = {'Authorization': f'Bearer {token}'}
    sim = client.post('/api/v1/simulation/run', headers=headers, json={'seed': 42, 'duration_hours': 1, 'zones': 3, 'vehicles': 2, 'orders_per_hour': 2}); demand = client.post('/api/v1/forecast/demand', headers=headers, json={'values': [4, 6, 8], 'horizon': 1}); strategies = client.get('/api/v1/routing/strategies', headers=headers)
    assert health.status_code == sim.status_code == demand.status_code == strategies.status_code == 200
    return {'forecast_value': forecast, 'route_cost': route.travel_cost if route else None, 'vehicle_rows': len(vehicle_dispatch_rows(snapshot)), 'api_statuses': [health.status_code, sim.status_code, demand.status_code, strategies.status_code]}

if __name__ == '__main__':
    import json
    print(json.dumps(main(), indent=2))
