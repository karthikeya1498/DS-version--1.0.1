import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.realtime.traffic_stream import traffic_stream
from src.security.auth import decode_token

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/traffic")
async def traffic_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    try:
        principal = decode_token(token)
    except Exception:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    queue = await traffic_stream.subscribe()
    try:
        await websocket.send_json({"event_type": "connected", "tenant_id": principal["tenant_id"]})
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=25)
            except TimeoutError:
                await websocket.send_json({"event_type": "heartbeat"})
                continue
            await websocket.send_json(event)
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        traffic_stream.unsubscribe(queue)
