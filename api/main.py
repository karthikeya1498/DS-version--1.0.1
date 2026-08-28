from fastapi import FastAPI

from api.routes.assistant import router as assistant_router
from api.routes.auth import router as auth_router
from api.routes.decisions import router as decisions_router
from api.routes.eta import router as eta_router
from api.routes.experiments import router as experiments_router
from api.routes.forecast import router as forecast_router
from api.routes.health import router as health_router
from api.routes.optimization import router as optimization_router
from api.routes.realtime import router as realtime_router
from api.routes.routing import router as routing_router
from api.routes.scenarios import router as scenarios_router
from api.routes.simulation import router as simulation_router
from api.routes.traffic import router as traffic_router
from src.common.config import get_settings
from src.common.logger import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="OPTIMA-X API", version="0.1.0", description="Decision and optimization engine API"
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(optimization_router, prefix="/api/v1")
app.include_router(forecast_router, prefix="/api/v1")
app.include_router(eta_router, prefix="/api/v1")
app.include_router(routing_router, prefix="/api/v1")
app.include_router(decisions_router, prefix="/api/v1")
app.include_router(experiments_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(assistant_router, prefix="/api/v1")
app.include_router(scenarios_router, prefix="/api/v1")
app.include_router(traffic_router, prefix="/api/v1")
app.include_router(realtime_router, prefix="/api/v1")


@app.middleware("http")
async def tenant_rate_limit_middleware(request, call_next):
    import os

    from fastapi.responses import JSONResponse

    from src.security.auth import decode_token
    from src.security.rate_limit import limiter

    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    tenant = "anonymous"
    public = request.url.path in {"/", "/api/v1/health", "/api/v1/auth/token"}
    if token:
        try:
            tenant = decode_token(token).get("tenant_id", tenant)
        except Exception:
            if os.getenv("AUTH_REQUIRED", "false").lower() == "true" and not public:
                return JSONResponse({"detail": "invalid JWT"}, status_code=401)
    elif os.getenv("AUTH_REQUIRED", "false").lower() == "true" and not public:
        return JSONResponse({"detail": "Bearer token required"}, status_code=401)
    request.state.tenant_id = tenant
    if not public:
        decision = await limiter.acquire(tenant)
        if not decision.allowed:
            return JSONResponse(
                {"detail": "rate limit exceeded"},
                status_code=429,
                headers={
                    "Retry-After": str(max(1, int(decision.retry_after + 0.999))),
                    "X-RateLimit-Limit": str(limiter.limit),
                    "X-RateLimit-Remaining": str(decision.remaining),
                },
            )
    return await call_next(request)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "optima-x-api", "docs": "/docs"}
