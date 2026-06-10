from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import HTTPException

from app.config.database import get_collection
from app.schemas.assign_operations_schemas import AssignOperationsRequest
from app.services.notification_service import notification_manager


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def assign_operations(payload: AssignOperationsRequest) -> Dict[str, Any]:
    users_col = await get_collection("users")
    operations_col = await get_collection("operations")
    sos_col = await get_collection("sos")
    assigns_col = await get_collection("assign_operations")

    # Validate team exists
    team = await users_col.find_one({"_id": ObjectId(payload.teamId)})

    if not team:
        raise HTTPException(status_code=404, detail="rescue_team user not found")

    # Validate operation exists
    op_doc = await operations_col.find_one({"_id": ObjectId(payload.operationId)})

    if not op_doc:
        raise HTTPException(status_code=404, detail="operation not found")

    # Build rescue_team_location for storage
    rescue_team_location = payload.rescue_team_location.model_dump()

    # Update Operations collection: assignId, rescue_team_location, status, taskStatus
    await operations_col.update_one(
        {"_id": op_doc["_id"]},
        {
            "$set": {
                "assignId": payload.teamId,
                "rescue_team_location": rescue_team_location,
                "status": "assigned",
                "taskStatus": "assigned",
                "updated_at": _utcnow(),
            }
        },
    )

    # Update SOS collection: set status to assigned
    # Get the sos_id from operation and update that specific SOS document
    sos_id = op_doc.get("sos_id")
    if sos_id:
        try:
            sos_object_id = ObjectId(sos_id)
            sos_doc = await sos_col.find_one({"_id": sos_object_id})
            
            if sos_doc:
                await sos_col.update_one(
                    {"_id": sos_object_id},
                    {"$set": {"status": "assigned", "updated_at": _utcnow()}},
                )
        except Exception:
            pass

    # Create assign_operations document (only metadata + generated id)
    # Keep response compatible with AssignOperationsDoc schema
    doc = {
        "teamId": payload.teamId,
        "operationId": payload.operationId,
        "rescue_team_location": rescue_team_location,
        "status": "assigned",
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }

    res = await assigns_col.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    
    # Send real-time notification to rescue team
    # Fetch SOS details for the notification
    if sos_id:
        try:
            sos_object_id = ObjectId(sos_id)
            sos_doc = await sos_col.find_one({"_id": sos_object_id})
            
            if sos_doc:
                await notification_manager.notify_assignment(
                    team_id=payload.teamId,
                    operation_id=str(op_doc["_id"]),
                    sos_id=sos_id,
                    sos_location=sos_doc.get("location", {}),
                    address=sos_doc.get("address", ""),
                    emergency_type=sos_doc.get("emergency_type", ""),
                    priority=sos_doc.get("priority", "high"),
                    mobile_no=sos_doc.get("mobile_no", ""),
                    additional_details=sos_doc.get("additional_details", ""),
                )
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    return doc

