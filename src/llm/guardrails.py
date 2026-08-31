"""Safety boundaries for controlled Phase 5 orchestration."""

from __future__ import annotations

from numbers import Number

from src.llm.schemas import ToolRequest

ALLOWED_TOOLS = frozenset(
    {
        "get_operational_state",
        "get_prediction",
        "optimize_scenario",
        "compare_solvers",
        "simulate_scenario",
        "get_decision_trace",
        "get_model_metrics",
        "get_experiment_result",
        "explain_route",
    }
)


def validate_tool_request(request: ToolRequest, depth: int = 0, max_depth: int = 3) -> ToolRequest:
    if depth >= max_depth:
        raise ValueError("maximum tool-call depth exceeded")
    if request.tool not in ALLOWED_TOOLS:
        raise ValueError(f"tool is not allowlisted: {request.tool}")
    if any(key.startswith(("write_", "delete_", "mutate_")) for key in request.arguments):
        raise ValueError("operational mutations are not permitted")
    return request


def grounded_numbers(values: dict[str, object], evidence: dict[str, Number]) -> bool:
    return all(
        not isinstance(value, Number) or key in evidence and float(value) == float(evidence[key])
        for key, value in values.items()
    )
