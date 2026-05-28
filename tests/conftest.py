from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.utils.dependencies import get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_verified_user(client, username: str, email: str, password: str) -> dict:
    client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )

    from app.utils.redis import get_verification_code

    code = get_verification_code(email)
    client.post("/auth/verify-email", json={"email": email, "code": code})

    login = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_token(client, username: str) -> str:
    response = client.post(
        "/auth/login", data={"username": username, "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_send_email():
    with patch("app.tasks.email_tasks.send_verification_email_task.delay") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_subscribe():
    async def fake_subscribe(user_id: int):
        pass

    with patch("app.utils.connection_manager.ConnectionManager.subscribe", side_effect=fake_subscribe):
        yield


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    return response.json()


@pytest.fixture
def verified_user(client, registered_user):
    from app.utils.redis import get_verification_code

    code = get_verification_code("test@example.com")
    client.post("/auth/verify-email", json={"email": "test@example.com", "code": code})
    return registered_user


@pytest.fixture
def auth_headers(client, verified_user):
    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
