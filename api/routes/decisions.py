from fastapi import APIRouter

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.post("/explain")
def explain(payload: dict):
    return {"explanation": "Structured decision explanation", "input": payload}
