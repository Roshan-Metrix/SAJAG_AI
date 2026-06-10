from __future__ import annotations

import json
from typing import Any, Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.rescue_team_location_service import (
    upsert_rescue_team_location,
)

from app.middleware.auth import verify_access_token

router = APIRouter(tags=["rescue-team-location"])


class ConnectionManager:
    def __init__(self):
        self.connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        dead_connections = []

        for ws in self.connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(ws)


manager = ConnectionManager()


@router.websocket("/ws/rescue-team-location")
async def rescue_team_location_ws(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = verify_access_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    user_id = str(payload.get("user_id"))
    role = payload.get("role")

    await manager.connect(websocket)

    try:
        while True:

            data = await websocket.receive_json()

            if role == "rescue_team":

                current_location = data.get("current_location")

                if not current_location:
                    continue

                document = await upsert_rescue_team_location(
                    rescue_team_id=user_id,
                    current_location=current_location,
                    accuracy=data.get("accuracy"),
                    heading=data.get("heading"),
                )

                await manager.broadcast(
                    {
                        "type": "location_update",
                        "rescue_team_id": user_id,
                        "location": current_location,
                        "accuracy": data.get("accuracy"),
                        "heading": data.get("heading"),
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        print("WebSocket Error:", e)
        manager.disconnect(websocket)