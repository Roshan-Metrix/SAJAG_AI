"""Schemas for geospatial operations and statistics."""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(..., min_items=2, max_items=2)


class NearbySosRequest(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    max_distance_km: int = Field(default=10, ge=1, le=50)
    limit: int = Field(default=20, ge=1, le=100)


class NearbySosItem(BaseModel):
    id: str = Field(..., alias="_id")
    location: dict
    address: str
    emergency_type: str
    priority: str
    status: str
    distance_km: float
    created_at: str

    class Config:
        populate_by_name = True


class NearbyRescueTeamRequest(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    max_distance_km: int = Field(default=15, ge=1, le=50)
    limit: int = Field(default=10, ge=1, le=100)


class NearbyRescueTeamItem(BaseModel):
    rescue_team_id: str
    team_name: str
    mobile_number: str
    distance_km: float
    current_location: dict
    updated_at: Optional[str] = None


class RescueTeamStatsResponse(BaseModel):
    rescue_team_id: str
    assigned: int
    in_progress: int
    pending: int
    completed: int
    total: int
    
class RescueTeamStatsForAdminResponse(BaseModel):
    not_assign: int
    assigned: int
    in_progress: int
    pending: int
    completed: int
    total: int


class OperationalStatisticsResponse(BaseModel):
    operations: dict
    sos: dict
    rescue_teams: dict
