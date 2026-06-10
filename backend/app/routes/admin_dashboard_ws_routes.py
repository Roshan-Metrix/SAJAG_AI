"""WebSocket routes for admin command center real-time dashboard."""
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from fastapi.encoders import jsonable_encoder

from app.middleware.auth import verify_access_token, require_role
from app.config.database import get_collection
from bson import ObjectId


from datetime import datetime
def serialize_mongo(obj):
    if isinstance(obj, ObjectId):
        return str(obj)

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {
            k: serialize_mongo(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            serialize_mongo(item)
            for item in obj
        ]

    return obj

router = APIRouter(tags=["admin-dashboard"])


class AdminDashboardManager:
    """Manages WebSocket connections for admin dashboard."""
    
    def __init__(self):
        self.connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)
    
    async def broadcast_operation_update(self, operation: dict):
        """Broadcast operation updates to all admin dashboards."""
        message = {
            "type": "operation_update",
            "operation": operation,
        }
        await self._broadcast(message)
    
    async def broadcast_sos_alert(self, sos: dict):
        """Broadcast new SOS alert to admins."""
        message = {
            "type": "sos_alert",
            "sos": sos,
        }
        await self._broadcast(message)
    
    async def broadcast_team_location_update(self, team_id: str, location: dict):
        """Broadcast rescue team location update."""
        message = {
            "type": "team_location_update",
            "team_id": team_id,
            "location": location,
        }
        await self._broadcast(message)
    
    async def broadcast_statistics_update(self, stats: dict):
        """Broadcast updated statistics."""
        message = {
            "type": "statistics_update",
            "statistics": stats,
        }
        await self._broadcast(message)
    
    async def _broadcast(self, message: dict):
        """Broadcast message to all connected admins."""
        dead_connections = []
        for ws in self.connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(ws)
        
        for ws in dead_connections:
            self.disconnect(ws)


admin_manager = AdminDashboardManager()


@router.websocket("/ws/admin-dashboard")
async def admin_dashboard_ws(websocket: WebSocket):
    """
    WebSocket for admin command center real-time dashboard.
    Streams all operations, team locations, and SOS alerts.
    
    Expected query params:
    - token: JWT token for admin authentication
    """
    
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=1008, reason="No token provided")
        return
    
    try:
        payload = verify_access_token(token)
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Check admin role
    if payload.get("role") != "admin":
        await websocket.close(code=1008, reason="Admin access required")
        return
    
    admin_id = str(payload.get("user_id"))
    
    await admin_manager.connect(websocket)
    
    try:
        while True:
            # Receive keep-alive or commands
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Admin can request live data snapshot
            elif data.get("type") == "request_snapshot":
                operations_col = await get_collection("operations")
                rescue_team_loc_col = await get_collection("rescue_team_location")
                
                # Get all active operations
                ops = []
                async for op in operations_col.find({"status": {"$ne": "completed"}}).limit(100):
                    ops.append(serialize_mongo(op))
                
                # Get all team locations
                teams = []
                async for team in rescue_team_loc_col.find({}).limit(100):
                    teams.append(serialize_mongo(team))
                
                await websocket.send_json({
                    "type": "snapshot",
                    "operations": ops,
                    "rescue_teams": teams,
                })
    
    except WebSocketDisconnect:
        admin_manager.disconnect(websocket)
    
    except Exception as e:
        print(f"Admin WebSocket Error: {e}")
        admin_manager.disconnect(websocket)
