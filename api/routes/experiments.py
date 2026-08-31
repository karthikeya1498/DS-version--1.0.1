from fastapi import APIRouter

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/status")
def status():
    return {"status": "ready", "tracking": "local", "reproducible": True}
