from io import BytesIO

from PIL import Image


def register_and_login(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_report(client, headers):
    response = client.post(
        "/reports",
        headers=headers,
        json={
            "category": "improper_parking",
            "description": "Test report",
            "latitude": 50.0647,
            "longitude": 19.945,
        },
    )

    return response.json()["id"]


def create_image(client, headers, report_id):
    image = Image.new(
        "RGB",
        (100, 100),
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    response = client.post(
        f"/reports/{report_id}/images",
        headers=headers,
        files={
            "file": (
                "test.jpg",
                buffer,
                "image/jpeg",
            )
        },
    )

    return response.json()["id"]


def test_create_analysis_with_detections(client):
    headers = register_and_login(client)

    report_id = create_report(
        client,
        headers,
    )

    image_id = create_image(
        client,
        headers,
        report_id,
    )

    response = client.post(
        f"/images/{image_id}/analyses",
        headers=headers,
        json={
            "model_name": "yolov8",
            "model_version": "mock",
            "inference_time_ms": 42.7,
            "detections": [
                {
                    "class_name": "car",
                    "confidence": 0.94,
                    "x1": 10.0,
                    "y1": 20.0,
                    "x2": 80.0,
                    "y2": 90.0,
                },
                {
                    "class_name": "person",
                    "confidence": 0.81,
                    "x1": 5.0,
                    "y1": 10.0,
                    "x2": 30.0,
                    "y2": 70.0,
                },
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["report_image_id"] == image_id
    assert data["model_name"] == "yolov8"
    assert data["model_version"] == "mock"
    assert data["inference_time_ms"] == 42.7

    assert len(data["detections"]) == 2

    assert data["detections"][0]["class_name"] == "car"
    assert data["detections"][0]["confidence"] == 0.94


def test_reject_invalid_confidence(client):
    headers = register_and_login(client)

    report_id = create_report(
        client,
        headers,
    )

    image_id = create_image(
        client,
        headers,
        report_id,
    )

    response = client.post(
        f"/images/{image_id}/analyses",
        headers=headers,
        json={
            "model_name": "yolov8",
            "model_version": "mock",
            "inference_time_ms": 20,
            "detections": [
                {
                    "class_name": "car",
                    "confidence": 1.5,
                    "x1": 10,
                    "y1": 20,
                    "x2": 80,
                    "y2": 90,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_user_cannot_analyse_another_users_image(client):
    headers_a = register_and_login(client)

    report_id = create_report(
        client,
        headers_a,
    )

    image_id = create_image(
        client,
        headers_a,
        report_id,
    )

    client.post(
        "/auth/register",
        json={
            "email": "second@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "second@example.com",
            "password": "password123",
        },
    )

    headers_b = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    response = client.post(
        f"/images/{image_id}/analyses",
        headers=headers_b,
        json={
            "model_name": "yolov8",
            "model_version": "mock",
            "inference_time_ms": 20,
            "detections": [],
        },
    )

    assert response.status_code == 404