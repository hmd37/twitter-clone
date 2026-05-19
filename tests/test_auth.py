def test_register_success(client):
    response = client.post("/users/register", json={
        "username": "ali",
        "email": "ali@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "ali"
    assert data["email"] == "ali@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_username(client, registered_user):
    response = client.post("/users/register", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "password123"
    })
    assert response.status_code == 400


def test_register_duplicate_email(client, registered_user):
    response = client.post("/users/register", json={
        "username": "differentuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 400


def test_login_success(client, verified_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_wrong_username(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "nobody",
        "password": "password123"
    })
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401


def test_protected_route_with_token(client, auth_headers):
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"