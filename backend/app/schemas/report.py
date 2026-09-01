from datetime import datetime

from pydantic import BaseModel, Field


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
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }