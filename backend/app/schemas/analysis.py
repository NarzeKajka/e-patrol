from datetime import datetime

from pydantic import BaseModel, Field


class DetectionCreate(BaseModel):
    class_name: str
    confidence: float = Field(ge=0, le=1)

    x1: float
    y1: float
    x2: float
    y2: float


class DetectionResponse(DetectionCreate):
    id: int
    analysis_id: int

    model_config = {
        "from_attributes": True
    }


class AnalysisCreate(BaseModel):
    model_name: str
    model_version: str | None = None
    inference_time_ms: float = Field(ge=0)

    detections: list[DetectionCreate] = []


class AnalysisResponse(BaseModel):
    id: int
    report_image_id: int
    model_name: str
    model_version: str | None
    inference_time_ms: float
    created_at: datetime

    detections: list[DetectionResponse]

    model_config = {
        "from_attributes": True
    }