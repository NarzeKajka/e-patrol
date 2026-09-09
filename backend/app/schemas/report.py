from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ReportStatus(str, Enum):
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class ReportCreate(BaseModel):
    category: str
    description: str | None = None

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )


class ReportResponse(BaseModel):
    id: int
    user_id: int
    category: str
    description: str | None
    latitude: float
    longitude: float
    status: ReportStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }