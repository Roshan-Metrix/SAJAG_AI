from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId

from app.config.database import get_collection


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_rescue_team_user(rescue_team_id: str) -> None:
    """Validate that rescue_team_id exists in users collection with role=rescue_team."""
    users_col = await get_collection("users")

    try:
        user_doc = await users_col.find_one({"_id": ObjectId(rescue_team_id)})
    except Exception:
        user_doc = None

    if not user_doc or user_doc.get("role") != "rescue_team":
        raise ValueError("rescue_team_id is invalid or user is not a rescue_team")


async def upsert_rescue_team_location(
    *,
    rescue_team_id: str,
    current_location: Dict[str, Any],
    accuracy: Optional[float] = None,
    heading: Optional[float] = None,
) -> Dict[str, Any]:
    """Upsert current location for a rescue team into rescue_team_location collection."""

    await ensure_rescue_team_user(rescue_team_id)

    col = await get_collection("rescue_team_location")

    now = _utcnow()

    update_doc: Dict[str, Any] = {
        "$set": {
            "rescue_team_id": rescue_team_id,
            "current_location": current_location,
            "updated_at": now,
        }
    }

    if accuracy is not None:
        update_doc["$set"]["accuracy"] = accuracy
    if heading is not None:
        update_doc["$set"]["heading"] = heading

    # one live doc per team (Uber-like)
    await col.update_one(
        {"rescue_team_id": rescue_team_id},
        update_doc,
        upsert=True,
    )

    return {
        "rescue_team_id": rescue_team_id,
        "current_location": current_location,
        "updated_at": now.isoformat(),
        "accuracy": accuracy,
        "heading": heading,
    }

