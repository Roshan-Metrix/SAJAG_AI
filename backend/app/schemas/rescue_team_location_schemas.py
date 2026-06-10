from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    # GeoJSON standard: [longitude, latitude]
    coordinates: List[float] = Field(..., min_items=2, max_items=2)


class RescueTeamLocationUpsertRequest(BaseModel):
    rescue_team_id: str
    current_location: GeoJSONPoint
    # optional metadata
    accuracy: Optional[float] = None
    heading: Optional[float] = None


class RescueTeamLocationBroadcast(BaseModel):
    rescue_team_id: str
    current_location: GeoJSONPoint
    updated_at: str
    accuracy: Optional[float] = None
    heading: Optional[float] = None

