from pathlib import Path
from time import perf_counter

from PIL import Image

from app.core.config import settings


# Kolejność musi odpowiadać plikowi data.yaml użytemu przy treningu:
#   0 = road_damage, 1 = waste, 2 = graffiti
CLASS_NAMES = [
    "road_damage",
    "waste",
    "graffiti",
]

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_NAME = "yolov8s"
MODEL_VERSION = "epatrol-v1"

INFERENCE_IMAGE_SIZE = 640
MAX_RETURNED_DETECTIONS = 10


_model = None


def get_model_path() -> Path:
    if settings.detection_model_path:
        return Path(settings.detection_model_path)

    return PROJECT_ROOT / "models" / "best.pt"


def load_model():
    global _model

    if _model is not None:
        return _model

    model_path = get_model_path()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Nie znaleziono pliku modelu: {model_path}. ")

    from ultralytics import YOLO

    _model = YOLO(str(model_path))

    return _model


def suggest_category(detections: list[dict]) -> str | None:
    if not detections:
        return None

    best_detection = max(
        detections,
        key=lambda detection: detection["confidence"],
    )

    return best_detection["class_name"]


def detect(image: Image.Image) -> dict:
    model = load_model()

    image_width, image_height = image.size

    started_at = perf_counter()

    results = model.predict(
        image,
        imgsz=INFERENCE_IMAGE_SIZE,
        conf=settings.detection_confidence_threshold,
        verbose=False,
    )

    inference_time_ms = (perf_counter() - started_at) * 1000

    boxes = results[0].boxes

    detections = []

    for index in range(len(boxes)):
        class_id = int(boxes.cls[index])

        if class_id >= len(CLASS_NAMES):
            continue

        x1, y1, x2, y2 = (
            float(value)
            for value in boxes.xyxy[index]
        )

        detections.append(
            {
                "class_name": CLASS_NAMES[class_id],
                "confidence": float(boxes.conf[index]),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            }
        )

    category = suggest_category(detections)

    detections.sort(
        key=lambda detection: detection["confidence"],
        reverse=True,
    )

    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "inference_time_ms": inference_time_ms,
        "image_width": image_width,
        "image_height": image_height,
        "suggested_category": category,
        "detections": detections[:MAX_RETURNED_DETECTIONS],
    }
