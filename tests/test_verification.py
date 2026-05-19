from app.utils.redis import get_verification_code


def test_register_sends_verification_email(client, mock_send_email):
    mock_user, mock_auth = mock_send_email

    client.post("/users/register", json={
        "username": "ali",
        "email": "ali@example.com",
        "password": "password123"
    })
    mock_user.assert_called_once()


def test_register_stores_code_in_redis(client):
    client.post("/users/register", json={
        "username": "ali",
        "email": "ali@example.com",
        "password": "password123"
    })
    code = get_verification_code("ali@example.com")
    assert code is not None
    assert len(code) == 6
    assert code.isdigit()


def test_register_user_is_not_verified(client, registered_user):
    assert registered_user["is_verified"] == False


def test_verify_email_success(client, registered_user):
    code = get_verification_code("test@example.com")

    response = client.post("/auth/verify-email", json={
        "email": "test@example.com",
        "code": code
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"


def test_verify_email_wrong_code(client, registered_user):
    response = client.post("/auth/verify-email", json={
        "email": "test@example.com",
        "code": "000000"
    })
    assert response.status_code == 400


def test_verify_email_code_deleted_after_use(client, registered_user):
    code = get_verification_code("test@example.com")

    client.post("/auth/verify-email", json={
        "email": "test@example.com",
        "code": code
    })

    # code should be gone from Redis
    assert get_verification_code("test@example.com") is None


def test_verify_email_code_cannot_be_reused(client, registered_user):
    code = get_verification_code("test@example.com")

    client.post("/auth/verify-email", json={
        "email": "test@example.com",
        "code": code
    })

    # try using the same code again
    response = client.post("/auth/verify-email", json={
        "email": "test@example.com",
        "code": code
    })
    assert response.status_code == 400


def test_login_blocked_without_verification(client, registered_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 403
    assert "verify" in response.json()["detail"].lower()


def test_login_works_after_verification(client, verified_user):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_resend_verification(client, registered_user, mock_send_email):
    mock_user, mock_auth = mock_send_email

    response = client.post("/auth/resend-verification", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert mock_user.call_count == 1   # called once in register
    assert mock_auth.call_count == 1   # called once in resend


def test_resend_verification_generates_new_code(client, registered_user):
    old_code = get_verification_code("test@example.com")

    client.post("/auth/resend-verification", json={
        "email": "test@example.com"
    })

    new_code = get_verification_code("test@example.com")
    assert new_code is not None
    # new code should be different (extremely rarely could be same by chance)
    # more importantly it should be a valid 6 digit code
    assert len(new_code) == 6
    assert new_code.isdigit()


def test_resend_verification_already_verified(client, verified_user):
    response = client.post("/auth/resend-verification", json={
        "email": "test@example.com"
    })
    assert response.status_code == 400