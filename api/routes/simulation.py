from datetime import timedelta

from fastapi import APIRouter

from api.schemas.requests import SimulationRequest
from src.simulation.models import SimulationConfig
from src.simulation.simulator import LogisticsSimulator

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run")
def run_simulation(request: SimulationRequest):
    config = SimulationConfig(
        seed=request.seed,
        duration=timedelta(hours=request.duration_hours),
        zones=request.zones,
        vehicles=request.vehicles,
        orders_per_hour=request.orders_per_hour,
    )
    return LogisticsSimulator(config).run().to_summary()
