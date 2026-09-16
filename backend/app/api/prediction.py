from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, ImageOps

from app.ai.detector import detect
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.prediction import PredictionResponse
from app.services.image_validator import validate_image


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_image(
    file: Annotated[
        UploadFile,
        File(),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):

    validate_image(file)

    contents = file.file.read()

    image = Image.open(BytesIO(contents))
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    try:
        result = detect(image)

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )

    return result
