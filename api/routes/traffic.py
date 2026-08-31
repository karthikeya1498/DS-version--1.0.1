import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.realtime.traffic_stream import traffic_stream
from src.security.auth import TenantPrincipal, get_current_principal

router = APIRouter(prefix="/traffic", tags=["traffic"])


class TrafficUpdate(BaseModel):
    """One zone-level traffic change emitted to route consumers."""

    zone_id: str
    multiplier: float
    affected_vehicle_ids: list[str] = Field(default_factory=list)


class TrafficUpdateBatch(BaseModel):
    """Bounded batch contract that amortizes HTTP and rate-limit overhead."""

    updates: list[TrafficUpdate] = Field(min_length=1, max_length=100)


async def _publish(principal: TenantPrincipal, update: TrafficUpdate) -> None:
    """Publish one tenant-scoped route-reoptimization event."""
    await traffic_stream.publish(
        "route_reoptimization",
        {
            "tenant_id": principal.tenant_id,
            "zone_id": update.zone_id,
            "multiplier": update.multiplier,
            "affected_vehicle_ids": update.affected_vehicle_ids,
            "action": "recompute_routes",
        },
    )


@router.post("/updates")
async def publish_update(
    update: TrafficUpdate, principal: TenantPrincipal = Depends(get_current_principal)
):
    """Publish one traffic update for backwards-compatible callers."""
    await _publish(principal, update)
    return {"accepted": True, "tenant_id": principal.tenant_id}


@router.post("/updates/batch")
async def publish_update_batch(
    batch: TrafficUpdateBatch, principal: TenantPrincipal = Depends(get_current_principal)
):
    """Publish a bounded batch concurrently while consuming one HTTP token."""
    await asyncio.gather(*(_publish(principal, update) for update in batch.updates))
    return {
        "accepted": len(batch.updates),
        "tenant_id": principal.tenant_id,
        "event_type": "route_reoptimization",
    }
