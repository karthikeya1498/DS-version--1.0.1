from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.realtime.traffic_stream import traffic_stream
from src.security.auth import TenantPrincipal, get_current_principal
router = APIRouter(prefix='/traffic', tags=['traffic'])
class TrafficUpdate(BaseModel): zone_id: str; multiplier: float; affected_vehicle_ids: list[str] = []
@router.post('/updates')
async def publish_update(update: TrafficUpdate, principal: TenantPrincipal = Depends(get_current_principal)):
    await traffic_stream.publish('route_reoptimization', {'tenant_id': principal.tenant_id, 'zone_id': update.zone_id, 'multiplier': update.multiplier, 'affected_vehicle_ids': update.affected_vehicle_ids, 'action': 'recompute_routes'})
    return {'accepted': True, 'tenant_id': principal.tenant_id}
