from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    seed: int = 42
    duration_hours: float = Field(8, gt=0)
    zones: int = Field(5, gt=0)
    vehicles: int = Field(10, gt=0)
    orders_per_hour: int = Field(20, gt=0)
