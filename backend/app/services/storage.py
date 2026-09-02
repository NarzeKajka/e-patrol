from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class LocalStorageService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file: UploadFile) -> str:
        extension = Path(file.filename or "").suffix.lower()

        stored_filename = f"{uuid4()}{extension}"
        destination = self.base_dir / stored_filename

        with destination.open("wb") as output_file:
            output_file.write(file.file.read())

        return stored_filename

    def delete(self, stored_filename: str) -> None:
        path = self.base_dir / stored_filename

        if path.exists():
            path.unlink()

    def get_path(self, stored_filename: str) -> Path:
        return self.base_dir / stored_filename


PROJECT_ROOT = Path(__file__).resolve().parents[3]

report_image_storage = LocalStorageService(
    PROJECT_ROOT / "uploads" / "reports"
)