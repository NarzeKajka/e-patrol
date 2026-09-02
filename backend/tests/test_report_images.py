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
            "category": "illegal_dumping",
            "description": "Test report",
            "latitude": 50.0647,
            "longitude": 19.945,
        },
    )

    return response.json()["id"]


def create_test_jpeg():
    image = Image.new(
        "RGB",
        (100, 100),
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
    )

    buffer.seek(0)

    return buffer


def test_upload_valid_jpeg(client):
    headers = register_and_login(client)
    report_id = create_report(client, headers)

    image = create_test_jpeg()

    response = client.post(
        f"/reports/{report_id}/images",
        headers=headers,
        files={
            "file": (
                "test.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["report_id"] == report_id
    assert data["original_filename"] == "test.jpg"
    assert data["content_type"] == "image/jpeg"
    assert "id" in data


def test_reject_fake_image(client):
    headers = register_and_login(client)
    report_id = create_report(client, headers)

    fake_image = BytesIO(
        b"this is definitely not a jpeg"
    )

    response = client.post(
        f"/reports/{report_id}/images",
        headers=headers,
        files={
            "file": (
                "fake.jpg",
                fake_image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 415

    assert response.json() == {
        "detail": "Uploaded file is not a valid image"
    }