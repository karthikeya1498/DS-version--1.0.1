"""Operational intelligence endpoints for Phase 8.

Author: Karthikeya
"""
from __future__ import annotations

import os

from fastapi import APIRouter

from src.observability.metrics import metrics_registry

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("/metrics")
def operational_metrics() -> dict[str, object]:
    return {"phase": 8, "metrics": metrics_registry.snapshot()}


@router.get("/readiness")
def readiness() -> dict[str, object]:
    database_url = os.getenv("DATABASE_URL", "")
    return {
        "status": "ready",
        "service": "optima-x-api",
        "version": "0.1.0",
        "phase": 8,
        "persistence": {
            "configured": bool(database_url),
            "engine": "PostgreSQL 16",
            "lineage_schema": "optima",
        },
        "contracts": ["OperationalState", "PredictionBundle", "OptimizationResult", "PolicyOutcome", "DecisionRecord", "RuntimeTelemetry", "BenchmarkEvidence", "OperationalIntelligence"],
    }
