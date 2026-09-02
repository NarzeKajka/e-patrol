from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.analysis import Analysis
from app.models.detection import Detection
from app.models.report import Report
from app.models.report_image import ReportImage
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse


router = APIRouter(
    prefix="/images",
    tags=["Analysis"],
)


@router.post(
    "/{image_id}/analyses",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis(
    image_id: int,
    analysis_data: AnalysisCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    statement = (
        select(ReportImage)
        .join(Report)
        .where(
            ReportImage.id == image_id,
            Report.user_id == current_user.id,
        )
    )

    report_image = db.scalar(statement)

    if report_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report image not found",
        )

    analysis = Analysis(
        report_image_id=report_image.id,
        model_name=analysis_data.model_name,
        model_version=analysis_data.model_version,
        inference_time_ms=analysis_data.inference_time_ms,
    )

    for detection_data in analysis_data.detections:
        detection = Detection(
            class_name=detection_data.class_name,
            confidence=detection_data.confidence,
            x1=detection_data.x1,
            y1=detection_data.y1,
            x2=detection_data.x2,
            y2=detection_data.y2,
        )

        analysis.detections.append(detection)

    db.add(analysis)
    db.commit()

    statement = (
        select(Analysis)
        .options(
            selectinload(Analysis.detections)
        )
        .where(Analysis.id == analysis.id)
    )

    return db.scalar(statement)