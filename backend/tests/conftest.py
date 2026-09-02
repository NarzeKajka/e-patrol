import os

from app.services.storage import LocalStorageService

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://epatrol:epatrol_dev@localhost:5432/epatrol_test"
)
os.environ["JWT_SECRET_KEY"] = (
    "test-secret-key-for-epatrol-at-least-32-bytes-long"
)
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = (
    "postgresql+psycopg://epatrol:epatrol_dev@localhost:5432/epatrol_test"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def override_report_image_storage(tmp_path, monkeypatch):
    test_storage = LocalStorageService(
        tmp_path / "uploads" / "reports"
    )

    monkeypatch.setattr(
        "app.api.reports.report_image_storage",
        test_storage,
    )