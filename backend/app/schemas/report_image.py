from datetime import datetime

from pydantic import BaseModel


class ReportImageResponse(BaseModel):
    id: int
    report_id: int
    original_filename: str | None
    content_type: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }