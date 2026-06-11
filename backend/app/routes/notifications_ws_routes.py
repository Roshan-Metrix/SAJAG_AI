"""WebSocket routes for real-time notifications."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.middleware.auth import verify_access_token
from app.services.notification_service import notification_manager

router = APIRouter(tags=["notifications"])


@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for rescue teams to receive real-time notifications.
    
    Expected query params:
    - token: JWT token for authentication
    
    Receives:
    - sos_assignment: New SOS assigned to team
    - status_update: Operation status change
    - operation_completed: Operation marked complete
    - emergency_alert: Emergency broadcast
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
    
    team_id = str(payload.get("user_id"))
    role = payload.get("role")
    
    # Only rescue teams and admins can connect
    if role not in ["rescue_team", "admin"]:
        await websocket.close(code=1008, reason="Insufficient permissions")
        return
    
    # Connect to notification manager
    await notification_manager.connect(team_id, websocket)
    
    try:
        while True:
            # Receive messages (keep-alive or acknowledgments)
            data = await websocket.receive_json()
            
            # Handle keep-alive ping
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            # Handle notification acknowledgments
            elif data.get("type") == "ack":
                # Log acknowledgment if needed
                notification_id = data.get("notification_id")
                # TODO: Optionally track which notifications were received
                pass
    
    except WebSocketDisconnect:
        notification_manager.disconnect(team_id, websocket)
    
    except Exception as e:
        print(f"WebSocket Error for team {team_id}: {e}")
        notification_manager.disconnect(team_id, websocket)
