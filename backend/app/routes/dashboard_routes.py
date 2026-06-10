"""REST API endpoints for web dashboard operations."""
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId

from app.config.database import get_collection
from app.middleware.auth import require_role
from app.services.geospatial_service import get_operational_statistics

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/operations", dependencies=[Depends(require_role("admin"))])
async def get_dashboard_operations(
    status: str = Query("active", enum=["active", "completed", "all"]),
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get all operations for dashboard with enhanced details.
    
    Active: not_assign or assigned
    Completed: status = completed
    All: all operations
    """
    operations_col = await get_collection("operations")
    rescue_team_loc_col = await get_collection("rescue_team_location")
    users_col = await get_collection("users")
    sos_col = await get_collection("sos")
    
    # Build query
    if status == "active":
        query = {"status": {"$in": ["not_assign", "assigned"]}}
    elif status == "completed":
        query = {"status": "completed"}
    else:
        query = {}
    
    cursor = operations_col.find(query).sort("created_at", -1).limit(limit)
    
    operations = []
    async for op in cursor:
        op["_id"] = str(op["_id"])
        
        # Enrich with SOS details
        if op.get("sos_id"):
            try:
                sos = await sos_col.find_one({"_id": ObjectId(op["sos_id"])})
                if sos:
                    op["sos_details"] = {
                        "address": sos.get("address"),
                        "emergency_type": sos.get("emergency_type"),
                        "priority": sos.get("priority"),
                        "mobile_no": sos.get("mobile_no"),
                    }
            except Exception:
                pass
        
        # Enrich with team details and live location
        if op.get("assignId"):
            try:
                team = await users_col.find_one({"_id": ObjectId(op["assignId"])})
                if team:
                    op["team_details"] = {
                        "name": team.get("full_name"),
                        "mobile": team.get("mobile_number"),
                    }
                
                # Get live location
                live_loc = await rescue_team_loc_col.find_one(
                    {"rescue_team_id": str(op["assignId"])}
                )
                if live_loc:
                    op["team_live_location"] = live_loc.get("current_location")
                    op["team_location_updated_at"] = live_loc.get("updated_at")
            except Exception:
                pass
        
        operations.append(op)
    
    return {
        "count": len(operations),
        "operations": operations,
    }


@router.get("/dashboard/sos-alerts", dependencies=[Depends(require_role("admin"))])
async def get_dashboard_sos_alerts(
    limit: int = Query(100, ge=1, le=500),
):
    """Get all active SOS alerts for dashboard."""
    sos_col = await get_collection("sos")
    
    cursor = sos_col.find({"status": {"$ne": "completed"}}).sort("created_at", -1).limit(limit)
    
    alerts = []
    async for sos in cursor:
        sos["_id"] = str(sos["_id"])
        alerts.append(sos)
    
    return {
        "count": len(alerts),
        "sos_alerts": alerts,
    }


@router.get("/dashboard/rescue-teams", dependencies=[Depends(require_role("admin"))])
async def get_dashboard_rescue_teams(
    limit: int = Query(100, ge=1, le=500),
):
    """Get all rescue teams with their current status and location."""
    users_col = await get_collection("users")
    rescue_team_loc_col = await get_collection("rescue_team_location")
    operations_col = await get_collection("operations")
    
    cursor = users_col.find({"role": "rescue_team"}).sort("full_name", 1).limit(limit)
    
    teams = []
    async for user in cursor:
        team_id = str(user["_id"])
        
        # Get live location
        loc = await rescue_team_loc_col.find_one({"rescue_team_id": team_id})
        
        # Get current assignment count
        assigned_count = await operations_col.count_documents({
            "assignId": team_id,
            "status": {"$in": ["not_assign", "assigned"]},
        })
        
        team_info = {
            "team_id": team_id,
            "name": user.get("full_name"),
            "mobile": user.get("mobile_number"),
            "current_location": loc.get("current_location") if loc else None,
            "location_updated_at": loc.get("updated_at").isoformat() if loc and loc.get("updated_at") else None,
            "active_missions": assigned_count,
            "is_online": bool(loc),  # Team is online if we have recent location
        }
        teams.append(team_info)
    
    return {
        "count": len(teams),
        "rescue_teams": teams,
    }


@router.get("/dashboard/summary", dependencies=[Depends(require_role("admin"))])
async def get_dashboard_summary():
    """Get dashboard summary statistics."""
    stats = await get_operational_statistics()
    return {
        "statistics": stats,
    }


@router.get("/dashboard/live-map-data", dependencies=[Depends(require_role("admin"))])
async def get_live_map_data():
    """
    Get all data needed for live map visualization.
    Includes: SOS locations, Rescue team locations, Operations.
    """
    sos_col = await get_collection("sos")
    rescue_team_loc_col = await get_collection("rescue_team_location")
    operations_col = await get_collection("operations")
    
    # Get active SOS
    sos_alerts = []
    async for sos in sos_col.find({"status": {"$ne": "completed"}}).limit(100):
        sos["_id"] = str(sos["_id"])
        sos_alerts.append({
            "id": sos["_id"],
            "location": sos.get("location"),
            "emergency_type": sos.get("emergency_type"),
            "priority": sos.get("priority"),
            "address": sos.get("address"),
        })
    
    # Get team locations
    team_locations = []
    async for team in rescue_team_loc_col.find({}).limit(100):
        team_locations.append({
            "team_id": team.get("rescue_team_id"),
            "location": team.get("current_location"),
            "updated_at": team.get("updated_at").isoformat() if team.get("updated_at") else None,
        })
    
    # Get active operations
    active_ops = []
    async for op in operations_col.find({"status": {"$in": ["not_assign", "assigned"]}}).limit(100):
        active_ops.append({
            "operation_id": str(op["_id"]),
            "sos_location": op.get("sos_location"),
            "status": op.get("status"),
            "taskStatus": op.get("taskStatus"),
            "assignId": op.get("assignId"),
        })
    
    return {
        "sos_alerts": sos_alerts,
        "team_locations": team_locations,
        "operations": active_ops,
    }
