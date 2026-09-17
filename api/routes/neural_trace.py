"""Neural activation trace API for the dashboard.

Author: Karthikeya
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.ml.demand.neural_trace import build_demo_trace

router = APIRouter(prefix="/neural", tags=["neural-trace"])


class NeuralTraceRequest(BaseModel):
    features: list[float] = Field(min_length=1, max_length=12)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)


@router.post("/trace")
def neural_trace(request: NeuralTraceRequest) -> dict[str, object]:
    try:
        return build_demo_trace(request.features, seed=request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


__all__ = ["router"]
