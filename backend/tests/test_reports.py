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


def test_create_report(client):
    headers = register_and_login(client)

    response = client.post(
        "/reports",
        headers=headers,
        json={
            "category": "illegal_dumping",
            "description": "Porzucone worki ze śmieciami.",
            "latitude": 50.0647,
            "longitude": 19.945,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "illegal_dumping"
    assert data["description"] == "Porzucone worki ze śmieciami."
    assert data["latitude"] == 50.0647
    assert data["longitude"] == 19.945
    assert data["status"] == "submitted"
    assert "id" in data
    assert "user_id" in data


def test_get_my_reports(client):
    headers = register_and_login(client)

    client.post(
        "/reports",
        headers=headers,
        json={
            "category": "damaged_infrastructure",
            "description": "Uszkodzony znak.",
            "latitude": 50.06,
            "longitude": 19.94,
        },
    )

    response = client.get(
        "/reports/my",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "damaged_infrastructure"


def test_get_report_by_id(client):
    headers = register_and_login(client)

    create_response = client.post(
        "/reports",
        headers=headers,
        json={
            "category": "improper_parking",
            "description": "Samochód blokuje chodnik.",
            "latitude": 50.07,
            "longitude": 19.95,
        },
    )

    report_id = create_response.json()["id"]

    response = client.get(
        f"/reports/{report_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == report_id


def test_report_requires_authentication(client):
    response = client.post(
        "/reports",
        json={
            "category": "illegal_dumping",
            "description": "Test",
            "latitude": 50.0,
            "longitude": 19.0,
        },
    )

    assert response.status_code in {401, 403}


def test_user_cannot_access_another_users_report(client):
    # User A
    headers_a = register_and_login(client)

    create_response = client.post(
        "/reports",
        headers=headers_a,
        json={
            "category": "illegal_dumping",
            "description": "Raport użytkownika A",
            "latitude": 50.0,
            "longitude": 19.0,
        },
    )

    report_id = create_response.json()["id"]

    # User B
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

    token_b = login_response.json()["access_token"]

    headers_b = {
        "Authorization": f"Bearer {token_b}"
    }

    response = client.get(
        f"/reports/{report_id}",
        headers=headers_b,
    )

    assert response.status_code == 404