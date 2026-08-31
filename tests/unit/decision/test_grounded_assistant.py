"""Unit tests for Grounded Decision Assistant and Live Tool Execution."""

from src.llm.agent import DecisionAssistant
from src.llm.schemas import ToolRequest
from src.llm.tools import default_registry


def test_decision_assistant_text_intent_and_real_simulation():
    assistant = DecisionAssistant()
    # Prompt with +20% demand and +10% traffic
    resp = assistant.from_text("Simulate what happens if 20% demand and 10% traffic increase")
    assert resp.grounded is True
    assert "simulate_scenario" in resp.tool_calls
    assert any("delivered_orders" in ev for ev in resp.evidence)


def test_compare_solvers_live_execution():
    registry = default_registry()
    req = ToolRequest(tool="compare_solvers", arguments={})
    res = registry.execute(req)

    assert res["grounded"] is True
    assert "comparison" in res
    assert "greedy" in res["comparison"]
    assert "greedy_2opt" in res["comparison"]
    assert "best_solver" in res


def test_explain_route_live_execution():
    registry = default_registry()
    req = ToolRequest(tool="explain_route", arguments={"route_id": "r_101"})
    res = registry.execute(req)

    assert res["grounded"] is True
    assert "r_101" in res["explanation"]
    assert res["evidence"]["capacity_feasible"] is True
