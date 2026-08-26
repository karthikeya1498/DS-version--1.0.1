from fastapi.testclient import TestClient
from api.main import app
client = TestClient(app)
def test_simulation_route_returns_summary():
    response = client.post('/api/v1/simulation/run', json={'seed': 42, 'duration_hours': 1, 'zones': 2, 'vehicles': 2, 'orders_per_hour': 2})
    assert response.status_code == 200
    assert response.json()['metrics']['total_orders'] == 2
def test_optimization_demo_returns_result():
    response = client.get('/api/v1/optimization/demo')
    assert response.status_code == 200
    assert response.json()['strategy'] == 'graph_dispatch'
