"""Phase 5 isolated what-if scenario endpoint."""

from fastapi import APIRouter

from src.llm.schemas import ScenarioModification

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/simulate")
def simulate(modification: ScenarioModification):
    return {
        "status": "validated",
        "isolated": True,
        "modification": modification.model_dump(),
        "baseline_mutated": False,
    }
