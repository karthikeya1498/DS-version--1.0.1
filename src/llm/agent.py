"""Evidence-grounded analytical assistant; no operational mutation is exposed."""
from __future__ import annotations

import re

from src.llm.schemas import AssistantResponse, ToolRequest
from src.llm.tools import ToolRegistry, default_registry


class DecisionAssistant:
    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or default_registry()

    def from_text(self, text: str) -> AssistantResponse:
        demand = float(re.search(r'(\d+(?:\.\d+)?)% demand', text, re.IGNORECASE).group(1)) / 100 + 1 if re.search(r'\d+(?:\.\d+)?% demand', text, re.IGNORECASE) else 1.0
        traffic = float(re.search(r'(\d+(?:\.\d+)?)% traffic', text, re.IGNORECASE).group(1)) / 100 + 1 if re.search(r'\d+(?:\.\d+)?% traffic', text, re.IGNORECASE) else 1.0
        request = ToolRequest(tool='simulate_scenario', arguments={'demand_multiplier': demand, 'traffic_multiplier': traffic})
        response = self.run(request)
        return response.model_copy(update={'answer': f'Parsed the request into an isolated scenario simulation: {response.answer}'})

    def run(self, request: ToolRequest) -> AssistantResponse:
        result = self.registry.execute(request)
        grounded = bool(result.get('grounded', result.get('status') != 'evidence_required'))
        answer = f"Tool {request.tool} returned a validated structured result." if grounded else f"Tool {request.tool} requires additional evidence before a numerical explanation can be made."
        return AssistantResponse(answer=answer, evidence=[f'{key}={value}' for key, value in result.items() if key != 'grounded'], tool_calls=[request.tool], grounded=grounded)
