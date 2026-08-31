"""Evaluate Phase 5 structured orchestration on a fixed known-answer set."""

from __future__ import annotations

import json
from pathlib import Path

from src.llm.agent import DecisionAssistant
from src.llm.schemas import ToolRequest


def main() -> None:
    assistant = DecisionAssistant()
    cases = [
        ToolRequest(tool="simulate_scenario", arguments={"demand_multiplier": 1.2}),
        ToolRequest(tool="compare_solvers", arguments={"algorithms": ["dijkstra", "astar"]}),
        ToolRequest(tool="get_operational_state"),
    ]
    results = []
    valid = successful = grounded = 0
    for case in cases:
        try:
            response = assistant.run(case)
            valid += 1
            successful += int(bool(response.tool_calls))
            grounded += int(response.grounded)
            results.append(
                {
                    "tool": case.tool,
                    "schema_valid": True,
                    "tool_success": bool(response.tool_calls),
                    "grounded": response.grounded,
                }
            )
        except (ValueError, TypeError) as exc:
            results.append(
                {
                    "tool": case.tool,
                    "schema_valid": False,
                    "tool_success": False,
                    "grounded": False,
                    "error": str(exc),
                }
            )
    text_response = assistant.from_text("Simulate a 25% demand spike and 30% traffic increase.")
    summary = {
        "cases": len(cases),
        "schema_valid_rate": valid / len(cases),
        "tool_success_rate": successful / len(cases),
        "grounded_rate": grounded / len(cases),
        "scenario_parse_grounded": text_response.grounded,
        "results": results,
    }
    output = Path("data/processed/phase5")
    output.mkdir(parents=True, exist_ok=True)
    (output / "evaluation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
