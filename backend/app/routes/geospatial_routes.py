"""Routes for geospatial queries and statistics."""
from fastapi import APIRouter, HTTPException, Query, Depends

from app.schemas.geospatial_schemas import (
    NearbySosRequest,
    NearbyRescueTeamRequest,
    RescueTeamStatsForAdminResponse,
    RescueTeamStatsResponse,
    OperationalStatisticsResponse,
)

from app.services.geospatial_service import (
    create_geospatial_indexes,
    find_nearby_sos,
    find_nearby_rescue_teams,
    get_rescue_team_stats,
    get_operational_statistics,
    get_rescue_team_stats_for_admin,
)

from app.middleware.auth import get_current_user

router = APIRouter(tags=["geospatial"])

# Track if indexes have been created
_indexes_created = False


async def _ensure_indexes():
    """Ensure geospatial indexes are created before queries."""
    global _indexes_created
    if not _indexes_created:
        await create_geospatial_indexes()
        _indexes_created = True


@router.post("/geospatial/nearby-sos")
async def get_nearby_sos(payload: NearbySosRequest):
    """
    Find nearby SOS alerts for rescue teams (Uber-like discovery).
    
    Query parameters:
    - longitude: Rescue team longitude
    - latitude: Rescue team latitude
    - max_distance_km: Search radius (default 10km)
    - limit: Max results (default 20)
    """
    try:
        # Ensure indexes are created
        await _ensure_indexes()
        
        sos_list = await find_nearby_sos(
            longitude=payload.longitude,
            latitude=payload.latitude,
            max_distance_m=payload.max_distance_km * 1000,
            limit=payload.limit,
            exclude_statuses=["completed"],
        )
        return {
            "success": True,
            "count": len(sos_list),
            "sos_alerts": sos_list,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geospatial/nearby-rescue-teams")
async def get_nearby_rescue_teams(payload: NearbyRescueTeamRequest):
    """
    Find nearby rescue teams for a SOS location (for admin assignment suggestions).
    
    Query parameters:
    - longitude: SOS longitude
    - latitude: SOS latitude
    - max_distance_km: Search radius (default 15km)
    - limit: Max results (default 10)
    """
    try:
        # Ensure indexes are created
        await _ensure_indexes()
        
        teams = await find_nearby_rescue_teams(
            longitude=payload.longitude,
            latitude=payload.latitude,
            max_distance_m=payload.max_distance_km * 1000,
            limit=payload.limit,
        )
        return {
            "success": True,
            "count": len(teams),
            "rescue_teams": teams,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rescue-teams/{team_id}/stats")
async def get_team_statistics(
    team_id: str,
    current_user: dict = Depends(get_current_user)
) -> RescueTeamStatsResponse:
    """
    Get statistics for a specific rescue team.
    
    Accessible by:
    - Admin (can view any team's stats)
    - Rescue team member (can only view their own stats)
    
    Returns:
    - assigned: Count of assigned SOS
    - in_progress: Count of in-progress rescues
    - pending: Count of pending tasks
    - completed: Count of completed missions
    """
    try:
        # Authorization: Check if user is admin or the team member requesting their own stats
        user_role = current_user.get("role")
        user_id = current_user.get("user_id")
        
        # Admin can view any team's stats
        if user_role == "admin":
            pass  # Allow access
        # Rescue team can only view their own stats
        elif user_role == "rescue_team":
            # Check if the team_id matches the user's ID
            if user_id != team_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only view your own team statistics"
                )
        else:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized to access team statistics"
            )
        
        # Ensure indexes are created
        await _ensure_indexes()
        
        stats = await get_rescue_team_stats(team_id)
        return RescueTeamStatsResponse(
            rescue_team_id=team_id,
            **stats
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rescue-teams/stats")
async def get_team_statistics_for_admin(
    current_user: dict = Depends(get_current_user)
) -> RescueTeamStatsForAdminResponse:
    """
    Get statistics of all rescue team.
    
    Accessible by:
    - Admin (can view any team's stats)
    
    Returns:
    - not_assigned: count non assigned 
    - assigned: Count of assigned SOS
    - in_progress: Count of in-progress rescues
    - pending: Count of pending tasks
    - completed: Count of completed missions
    """
    try:
        # Authorization: Check if user is admin or the team member requesting their own stats
        user_role = current_user.get("role")
        user_id = current_user.get("user_id")
        
        # Admin can view any team's stats
        if user_role == "admin":
            pass  # Allow access
        else:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized to access team statistics"
            )
        
        # Ensure indexes are created
        await _ensure_indexes()
        
        stats = await get_rescue_team_stats_for_admin()
        return RescueTeamStatsForAdminResponse(
            **stats
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/operational")
async def get_statistics() -> OperationalStatisticsResponse:
    """
    Get overall operational statistics for the command center dashboard.
    
    Returns:
    - operations: Breakdown by status
    - sos: Breakdown by status
    - rescue_teams: Active vs total teams
    """
    try:
        # Ensure indexes are created
        await _ensure_indexes()
        
        stats = await get_operational_statistics()
        return OperationalStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geospatial/create-indexes")
async def create_indexes():
    """
    Manually create geospatial indexes (debugging endpoint).
    Call this if geospatial queries are failing with index errors.
    """
    try:
        await create_geospatial_indexes()
        return {
            "success": True,
            "message": "Geospatial indexes created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
