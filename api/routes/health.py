from fastapi import APIRouter

from api.schemas.responses import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="optima-x-api", version="0.1.0")
