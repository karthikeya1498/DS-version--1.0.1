"""Allowlisted, deterministic tools for Phase 5 decision intelligence."""
from __future__ import annotations

from collections.abc import Callable

from src.llm.guardrails import validate_tool_request
from src.llm.schemas import ScenarioModification, ToolRequest


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[dict], dict]] = {}
        self._evidence: dict[str, dict] = {}

    def register(self, name: str, handler: Callable[[dict], dict]) -> None:
        self._handlers[name] = handler

    def add_evidence(self, key: str, value: dict) -> None:
        self._evidence[key] = value

    def execute(self, request: ToolRequest) -> dict:
        validate_tool_request(request)
        if request.tool in self._handlers:
            return self._handlers[request.tool](request.arguments)
        if request.tool == 'get_decision_trace':
            return self._evidence.get(request.arguments.get('decision_id', ''), {'found': False})
        if request.tool == 'get_experiment_result':
            return self._evidence.get(request.arguments.get('experiment_id', ''), {'found': False})
        if request.tool == 'get_model_metrics':
            return self._evidence.get('model_metrics', {'found': False})
        if request.tool == 'get_operational_state':
            return self._evidence.get('operational_state', {'found': False})
        raise ValueError(f'no handler registered for {request.tool}')

def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register('simulate_scenario', lambda arguments: {'scenario_modification': ScenarioModification.model_validate(arguments).model_dump(), 'isolated': True, 'status': 'validated'})
    registry.register('compare_solvers', lambda arguments: {'comparison': arguments, 'status': 'validated', 'grounded': True})
    registry.register('optimize_scenario', lambda arguments: {'scenario_id': arguments.get('scenario_id', 'demo'), 'status': 'validated', 'grounded': True})
    registry.register('explain_route', lambda arguments: {'route_id': arguments.get('route_id'), 'status': 'evidence_required', 'grounded': False})
    registry.register('get_prediction', lambda arguments: registry._evidence.get(arguments.get('prediction_id', ''), {'found': False}))
    return registry
