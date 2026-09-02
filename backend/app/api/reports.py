from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportResponse
from app.models.report_image import ReportImage
from app.schemas.report_image import ReportImageResponse
from app.services.storage import report_image_storage
from app.services.image_validator import validate_image


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_data: ReportCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    report = Report(
        user_id=current_user.id,
        category=report_data.category,
        description=report_data.description,
        latitude=report_data.latitude,
        longitude=report_data.longitude,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get(
    "/my",
    response_model=list[ReportResponse],
)
def get_my_reports(
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
        select(Report)
        .where(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
    )

    reports = db.scalars(statement).all()

    return reports


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    statement = select(Report).where(
        Report.id == report_id,
        Report.user_id == current_user.id,
    )

    report = db.scalar(statement)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


@router.post(
    "/{report_id}/images",
    response_model=ReportImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_report_image(
    report_id: int,
    file: Annotated[
        UploadFile,
        File(),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    report = db.scalar(
        select(Report).where(
            Report.id == report_id,
            Report.user_id == current_user.id,
        )
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    validate_image(file)

    storage_key = report_image_storage.save(file)

    report_image = ReportImage(
        report_id=report.id,
        storage_key=storage_key,
        original_filename=file.filename,
        content_type=file.content_type,
    )

    db.add(report_image)
    db.commit()
    db.refresh(report_image)

    return report_image