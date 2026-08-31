"""Pydantic schemas for safe, structured Phase 5 orchestration."""
from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    tool: str = Field(min_length=1)
    arguments: dict = Field(default_factory=dict)

class ScenarioModification(BaseModel):
    demand_multiplier: float = Field(default=1.0, ge=0.0, le=5.0)
    traffic_multiplier: float = Field(default=1.0, ge=0.0, le=5.0)
    unavailable_vehicle_ids: list[str] = Field(default_factory=list)
    lateness_weight: float | None = Field(default=None, ge=0.0, le=1000.0)

class AssistantResponse(BaseModel):
    answer: str
    evidence: list[str] = Field(default_factory=list)
    tool_calls: list[str] = Field(default_factory=list)
    grounded: bool = True
