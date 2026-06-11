"""Routes for rescue team mission management."""
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone

from app.config.database import get_collection
from app.middleware.auth import require_role
from pydantic import BaseModel
from typing import Literal

router = APIRouter(tags=["mission"])


class MissionActionRequest(BaseModel):
    action: Literal["accept", "reject", "start", "reached", "completed"]


async def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@router.post("/missions/{operation_id}/action")
async def mission_action(
    operation_id: str,
    payload: MissionActionRequest,
    current_user: dict = Depends(require_role("rescue_team")),
):
    """
    Rescue team action on a mission.
    
    Actions:
    - accept: Accept the assigned mission
    - reject: Reject the assigned mission
    - start: Start moving to location
    - reached: Reached the victim location
    - completed: Mission completed, victim safe
    """
    
    team_id = current_user.get("user_id")
    operations_col = await get_collection("operations")
    
    try:
        op_oid = ObjectId(operation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid operation ID")
    
    op_doc = await operations_col.find_one({"_id": op_oid})
    
    if not op_doc:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    # Verify team is assigned to this operation
    if str(op_doc.get("assignId")) != team_id:
        raise HTTPException(status_code=403, detail="Not assigned to this mission")
    
    now = await _utcnow()
    current_status = op_doc.get("taskStatus")
    
    # Validate state transitions
    if payload.action == "accept":
        if current_status != "assigned":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot accept mission in {current_status} state"
            )
        new_status = "accepted"
    
    elif payload.action == "reject":
        if current_status not in ["assigned", "accepted"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject mission in {current_status} state"
            )
        new_status = "rejected"
    
    elif payload.action == "start":
        if current_status not in ["assigned", "accepted"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start mission in {current_status} state"
            )
        new_status = "on_the_way"
    
    elif payload.action == "reached":
        if current_status != "on_the_way":
            raise HTTPException(
                status_code=400,
                detail=f"Must be on_the_way before reaching"
            )
        new_status = "reached"
    
    elif payload.action == "completed":
        if current_status not in ["reached", "rescue_started"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete mission in {current_status} state"
            )
        new_status = "completed"
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Update operation
    await operations_col.update_one(
        {"_id": op_oid},
        {
            "$set": {
                "taskStatus": new_status,
                "status": "completed" if new_status == "completed" else "assigned",
                "updated_at": now,
            }
        },
    )
    
    # If rejected, unassign the operation
    if payload.action == "reject":
        await operations_col.update_one(
            {"_id": op_oid},
            {
                "$set": {
                    "assignId": None,
                    "status": "not_assign",
                    "taskStatus": "not_assign",
                    "updated_at": now,
                }
            },
        )
        
        # Also revert SOS status
        sos_id = op_doc.get("sos_id")
        if sos_id:
            try:
                sos_oid = ObjectId(sos_id)
                sos_col = await get_collection("sos")
                await sos_col.update_one(
                    {"_id": sos_oid},
                    {"$set": {"status": "not_assign", "updated_at": now}},
                )
            except Exception:
                pass
    
    # If completed, delete SOS
    elif payload.action == "completed":
        sos_id = op_doc.get("sos_id")
        if sos_id:
            try:
                sos_oid = ObjectId(sos_id)
                sos_col = await get_collection("sos")
                await sos_col.delete_one({"_id": sos_oid})
            except Exception:
                pass
    
    else:
        # Update SOS status to match operation
        sos_id = op_doc.get("sos_id")
        if sos_id:
            try:
                sos_oid = ObjectId(sos_id)
                sos_col = await get_collection("sos")
                await sos_col.update_one(
                    {"_id": sos_oid},
                    {"$set": {"status": new_status, "updated_at": now}},
                )
            except Exception:
                pass
    
    # Send notification
    from app.services.notification_service import notification_manager
    await notification_manager.notify_status_update(
        team_id=team_id,
        operation_id=operation_id,
        old_status=current_status,
        new_status=new_status,
    )
    
    return {
        "success": True,
        "message": f"Mission {payload.action}ed successfully",
        "operation_id": operation_id,
        "new_status": new_status,
    }


@router.get("/missions", dependencies=[Depends(require_role("rescue_team"))])
async def get_my_missions(
    current_user: dict = Depends(require_role("rescue_team")),
    status: str = None,
):
    """
    Get missions assigned to the current rescue team.
    
    Status filter options:
    - assigned: Not yet accepted
    - accepted: Accepted but not started
    - in_progress: On the way or at location
    - completed: Completed missions
    """
    
    team_id = current_user.get("user_id")
    operations_col = await get_collection("operations")
    
    # Build query
    query = {"assignId": team_id}
    
    if status == "assigned":
        query["taskStatus"] = "assigned"
    elif status == "accepted":
        query["taskStatus"] = "accepted"
    elif status == "in_progress":
        query["taskStatus"] = {"$in": ["on_the_way", "reached", "rescue_started"]}
    elif status == "completed":
        query["taskStatus"] = "completed"
    
    cursor = operations_col.find(query).sort("created_at", -1)
    
    missions = []
    async for op in cursor:
        op["_id"] = str(op["_id"])
        missions.append(op)
    
    return {
        "count": len(missions),
        "missions": missions,
    }
