"""Phase 5 decision-intelligence API endpoints."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.decision.contracts import CandidateEvidence, DecisionRecord
from src.decision.explanation_builder import explain_record
from src.decision.store import store

router = APIRouter(prefix="/decisions", tags=["decisions"])


class DecisionCreate(BaseModel):
    decision_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    selected_action: str = Field(min_length=1)
    objective_metrics: dict[str, float] = Field(default_factory=dict)
    candidates: list[CandidateEvidence] = Field(default_factory=list)
    dataset_version: str = "unknown"
    solver_version: str = "phase3"


@router.post("/record")
def record(payload: DecisionCreate):
    decision = DecisionRecord(
        decision_id=payload.decision_id,
        scenario_id=payload.scenario_id,
        state_reference="",
        dataset_version=payload.dataset_version,
        model_versions={},
        solver_version=payload.solver_version,
        rl_policy_version="",
        selected_action=payload.selected_action,
        objective_metrics=payload.objective_metrics,
        candidates=tuple(payload.candidates),
    )
    store.save(decision)
    return {"decision_id": decision.decision_id, "stored": True}


@router.get("/{decision_id}")
def get_decision(decision_id: str):
    decision = store.get(decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return asdict(decision)


@router.post("/explain")
def explain(payload: dict):
    decision = store.get(payload.get("decision_id", ""))
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return explain_record(decision)


@router.post("/compare")
def compare(payload: dict):
    decision = store.get(payload.get("decision_id", ""))
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return {
        "decision_id": decision.decision_id,
        "candidates": [asdict(candidate) for candidate in decision.candidates],
        "selected_action": decision.selected_action,
    }
