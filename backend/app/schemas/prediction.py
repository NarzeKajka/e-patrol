from pydantic import BaseModel, ConfigDict, Field


class PredictedDetection(BaseModel):
    class_name: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    x1: float
    y1: float
    x2: float
    y2: float


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    model_version: str | None = None

    inference_time_ms: float

    image_width: int
    image_height: int

    suggested_category: str | None = None

    detections: list[PredictedDetection] = []
