"""
Geospatial service for finding nearby SOS alerts and rescue teams.
Uses MongoDB geospatial indexes and queries.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from math import radians, cos, sin, asin, sqrt
from bson import ObjectId

from app.config.database import get_collection


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate great circle distance between two points on earth (in km).
    Coordinates in [longitude, latitude] format.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


async def create_geospatial_indexes() -> None:
    """Create 2dsphere indexes for geospatial queries."""
    try:
        sos_col = await get_collection("sos")
        rescue_team_loc_col = await get_collection("rescue_team_location")
        operations_col = await get_collection("operations")
        
        # Create 2dsphere index for SOS locations
        try:
            await sos_col.create_index([("location", "2dsphere")])
            print("[OK] Created geospatial index on sos.location")
        except Exception as e:
            print(f"[WARN] Could not create index on sos.location: {e}")
        
        # Create 2dsphere index for rescue team locations
        try:
            await rescue_team_loc_col.create_index([("current_location", "2dsphere")])
            print("[OK] Created geospatial index on rescue_team_location.current_location")
        except Exception as e:
            print(f"[WARN] Could not create index on rescue_team_location.current_location: {e}")
        
        # Create 2dsphere index for operations SOS location
        try:
            await operations_col.create_index([("sos_location", "2dsphere")])
            print("[OK] Created geospatial index on operations.sos_location")
        except Exception as e:
            print(f"[WARN] Could not create index on operations.sos_location: {e}")
    
    except Exception as e:
        print(f"[ERROR] Failed to create geospatial indexes: {e}")


async def find_nearby_sos(
    longitude: float,
    latitude: float,
    max_distance_m: int = 10000,  # Default 10km
    limit: int = 20,
    exclude_statuses: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Find nearby SOS alerts within max_distance.
    
    Args:
        longitude, latitude: Starting point (rescue team location)
        max_distance_m: Maximum distance in meters
        limit: Max results to return
        exclude_statuses: Statuses to exclude (e.g., ["completed", "in_progress"])
    
    Returns:
        List of nearby SOS documents sorted by distance
    """
    sos_col = await get_collection("sos")
    
    if exclude_statuses is None:
        exclude_statuses = []
    
    # GeoJSON Point query: [longitude, latitude]
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance_m,
            }
        },
        "status": {"$nin": exclude_statuses}
    }
    
    cursor = sos_col.find(query).limit(limit)
    
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Calculate distance for reference
        sos_coords = doc.get("location", {}).get("coordinates", [0, 0])
        distance_km = haversine(longitude, latitude, sos_coords[0], sos_coords[1])
        doc["distance_km"] = round(distance_km, 2)
        results.append(doc)
    
    return results


async def find_nearby_rescue_teams(
    longitude: float,
    latitude: float,
    max_distance_m: int = 15000,  # Default 15km
    limit: int = 10,
    exclude_team_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Find nearby rescue teams within max_distance.
    
    Args:
        longitude, latitude: SOS location
        max_distance_m: Maximum distance in meters
        limit: Max results to return
        exclude_team_ids: Team IDs to exclude from results
    
    Returns:
        List of nearby rescue teams sorted by distance
    """
    rescue_team_loc_col = await get_collection("rescue_team_location")
    
    if exclude_team_ids is None:
        exclude_team_ids = []
    
    # Convert string IDs to ObjectIds if needed
    exclude_ids = []
    for team_id in exclude_team_ids:
        try:
            exclude_ids.append(ObjectId(team_id))
        except Exception:
            exclude_ids.append(team_id)
    
    # GeoJSON Point query
    query = {
        "current_location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "$maxDistance": max_distance_m,
            }
        }
    }
    
    if exclude_ids:
        # Query to exclude teams already assigned (fetch from operations)
        operations_col = await get_collection("operations")
        assigned_teams = await operations_col.distinct(
            "assignId",
            {"status": {"$in": ["assigned", "not_assign"]}}
        )
        # Convert to ObjectIds
        assigned_team_oids = []
        for team_id in assigned_teams:
            if team_id:
                try:
                    if isinstance(team_id, str):
                        assigned_team_oids.append(ObjectId(team_id))
                    else:
                        assigned_team_oids.append(team_id)
                except Exception:
                    pass
        
        if assigned_team_oids:
            query["rescue_team_id"] = {
                "$nin": [str(tid) for tid in assigned_team_oids]
            }
    
    cursor = rescue_team_loc_col.find(query).limit(limit)
    
    results = []
    async for doc in cursor:
        team_coords = doc.get("current_location", {}).get("coordinates", [0, 0])
        distance_km = haversine(longitude, latitude, team_coords[0], team_coords[1])
        
        # Enrich with team info
        users_col = await get_collection("users")
        team_info = await users_col.find_one(
            {"_id": ObjectId(doc["rescue_team_id"])}
        )
        
        result = {
            "rescue_team_id": doc["rescue_team_id"],
            "current_location": doc.get("current_location"),
            "distance_km": round(distance_km, 2),
            "team_name": team_info.get("full_name", "") if team_info else "Unknown",
            "mobile_number": team_info.get("mobile_number", "") if team_info else "",
            "updated_at": doc.get("updated_at"),
        }
        results.append(result)
    
    return results


async def get_rescue_team_stats_for_admin() -> Dict[str, int]:
    """Get statistics of team for ADMIN."""
    
    operations_col = await get_collection("operations")
    
    # Count by task status - use assignId field (string)
    not_assign_count = await operations_col.count_documents({
        "taskStatus": "not_assign"
    })
    
    
    assigned_count = await operations_col.count_documents({
        "taskStatus": "assigned"
    })
    
    
    in_progress_count = await operations_col.count_documents({
        "taskStatus": {"$in": ["accepted","on_the_way","reached", "rescue_started","victim_safe"]}
    })
    
    pending_count = await operations_col.count_documents({
        "taskStatus": "not_assign"
    })
    
    completed_count = await operations_col.count_documents({
        "taskStatus": "completed"
    })
    
    return {
        "not_assign": not_assign_count,
        "assigned": assigned_count,
        "in_progress": in_progress_count,
        "pending": pending_count,
        "completed": completed_count,
        "total": assigned_count + in_progress_count + pending_count + completed_count,
    }

async def get_rescue_team_stats(rescue_team_id: str) -> Dict[str, int]:
    """Get statistics for a rescue team."""
    team_id = str(rescue_team_id)
    
    operations_col = await get_collection("operations")
    
    # Count by task status - use assignId field (string)
    assigned_count = await operations_col.count_documents({
        "assignId": team_id,
        "taskStatus": "assigned"
    })
    
    
    in_progress_count = await operations_col.count_documents({
        "assignId": team_id,
        "taskStatus": {"$in": ["accepted","on_the_way","reached", "rescue_started","victim_safe"]}
    })
    
    pending_count = await operations_col.count_documents({
        "assignId": team_id,
        "taskStatus": "not_assign"
    })
    
    completed_count = await operations_col.count_documents({
        "assignId": team_id,
        "taskStatus": "completed"
    })
    
    return {
        "assigned": assigned_count,
        "in_progress": in_progress_count,
        "pending": pending_count,
        "completed": completed_count,
        "total": assigned_count + in_progress_count + pending_count + completed_count,
    }


async def get_operational_statistics() -> Dict[str, Any]:
    """Get overall system statistics."""
    operations_col = await get_collection("operations")
    sos_col = await get_collection("sos")
    users_col = await get_collection("users")
    
    # Count operations by status
    not_assigned = await operations_col.count_documents({"status": "not_assign"})
    assigned = await operations_col.count_documents({"status": "assigned"})
    completed = await operations_col.count_documents({"status": "completed"})
    
    # Count SOS by status
    sos_not_assigned = await sos_col.count_documents({"status": "not_assign"})
    sos_assigned = await sos_col.count_documents({"status": "assigned"})
    
    # Count active teams (with recent location updates)
    from datetime import timedelta
    recent_threshold = _utcnow() - timedelta(hours=1)
    
    rescue_team_loc_col = await get_collection("rescue_team_location")
    active_teams = await rescue_team_loc_col.count_documents({
        "updated_at": {"$gt": recent_threshold}
    })
    
    total_teams = await users_col.count_documents({"role": "rescue_team"})
    
    return {
        "operations": {
            "not_assigned": not_assigned,
            "assigned": assigned,
            "completed": completed,
            "total": not_assigned + assigned + completed,
        },
        "sos": {
            "not_assigned": sos_not_assigned,
            "assigned": sos_assigned,
            "total": sos_not_assigned + sos_assigned,
        },
        "rescue_teams": {
            "active": active_teams,
            "total": total_teams,
        }
    }
