from fastapi.testclient import TestClient

from api.main import app
from src.decision.candidate_ranker import select_candidate
from src.decision.contracts import CandidateEvidence, DecisionRecord
from src.decision.counterfactual import ScenarioModification, apply_modification
from src.decision.explanation_builder import explain_record
from src.llm.guardrails import validate_tool_request
from src.llm.schemas import ToolRequest


def test_candidate_ranker_prefers_lowest_feasible_objective():
    candidates = [CandidateEvidence('b', 'b', True, 2.0), CandidateEvidence('a', 'a', False, 0.1, 'capacity')]
    assert select_candidate(candidates).candidate_id == 'b'


def test_counterfactual_isolated_from_baseline():
    baseline = {'demand': {'zone-a': 10}, 'traffic': {'zone-a': 1.0}}
    modified = apply_modification(baseline, ScenarioModification(demand_multiplier=1.2, traffic_multiplier=1.3))
    assert baseline['demand']['zone-a'] == 10
    assert modified['demand']['zone-a'] == 12
    assert modified['isolated'] is True


def test_explanation_is_grounded_in_record():
    record = DecisionRecord('d1', 's1', 'state-hash', 'data-v1', {'demand': 'm1'}, 'solver-v1', '', 'serve', {'cost': 4.0}, (CandidateEvidence('a', 'serve', True, 4.0), CandidateEvidence('b', 'defer', False, 9.0, 'late'),))
    explanation = explain_record(record)
    assert explanation['grounded'] is True
    assert 'cost=4.0' in explanation['evidence']
    assert 'defer: rejected (late)' in explanation['alternatives']


def test_guardrails_reject_mutation_and_unknown_tools():
    try:
        validate_tool_request(ToolRequest(tool='delete_orders'))
        assert False
    except ValueError:
        pass
    try:
        validate_tool_request(ToolRequest(tool='simulate_scenario', arguments={'mutate_state': True}))
        assert False
    except ValueError:
        pass


def test_assistant_parses_isolated_scenario_request():
    client = TestClient(app)
    response = client.post('/api/v1/assistant/query', json={'text': 'Simulate a 25% demand spike and 30% traffic increase.'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['grounded'] is True
    assert payload['tool_calls'] == ['simulate_scenario']
    assert 'isolated' in payload['evidence'][1]


def test_phase5_api_record_explain_and_scenario():
    client = TestClient(app)
    response = client.post('/api/v1/decisions/record', json={'decision_id': 'api-d1', 'scenario_id': 'api-s1', 'selected_action': 'serve', 'objective_metrics': {'cost': 3.0}})
    assert response.status_code == 200
    assert client.post('/api/v1/decisions/explain', json={'decision_id': 'api-d1'}).json()['grounded'] is True
    scenario = client.post('/api/v1/scenarios/simulate', json={'demand_multiplier': 1.25})
    assert scenario.status_code == 200 and scenario.json()['baseline_mutated'] is False
