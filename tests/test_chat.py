import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import create_verified_user, get_token


def test_websocket_connect(client, verified_user):
    token = get_token(client, "testuser")
    with client.websocket_connect(f"/ws/{token}") as ws:
        assert ws is not None


def test_websocket_invalid_token(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/invalidtoken") as ws:
            pass
    assert exc_info.value.code == 4001


def test_send_message(client, verified_user):
    # create second user
    create_verified_user(client, "sara", "sara@example.com", "password123")

    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "sara", "content": "hello sara"})
        response = ws.receive_json()

        assert response["content"] == "hello sara"
        assert response["from"] == "testuser"
        assert response["to"] == "sara"
        assert response["sent"] == True


def test_send_message_saves_to_database(client, verified_user, auth_headers):
    create_verified_user(client, "sara", "sara@example.com", "password123")

    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "sara", "content": "hello sara"})
        ws.receive_json()  

    # check message is in database via REST endpoint
    response = client.get("/conversations/sara", headers=auth_headers)
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["content"] == "hello sara"


def test_send_message_to_nonexistent_user(client, verified_user):
    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "nobody", "content": "hello"})
        response = ws.receive_json()
        assert "error" in response


def test_send_message_too_long(client, verified_user):
    create_verified_user(client, "sara", "sara@example.com", "password123")

    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "sara", "content": "x" * 1001})
        response = ws.receive_json()
        assert "error" in response


def test_send_message_missing_fields(client, verified_user):
    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"content": "hello"})  # missing "to"
        response = ws.receive_json()
        assert "error" in response


def test_get_conversations_empty(client, auth_headers):
    response = client.get("/conversations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_conversations(client, verified_user, auth_headers):
    create_verified_user(client, "sara", "sara@example.com", "password123")

    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "sara", "content": "hey"})
        ws.receive_json()

    response = client.get("/conversations", headers=auth_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == "sara"


def test_get_conversation_history(client, verified_user, auth_headers):
    create_verified_user(client, "sara", "sara@example.com", "password123")

    token = get_token(client, "testuser")

    with client.websocket_connect(f"/ws/{token}") as ws:
        ws.send_json({"to": "sara", "content": "first message"})
        ws.receive_json()
        ws.send_json({"to": "sara", "content": "second message"})
        ws.receive_json()

    response = client.get("/conversations/sara", headers=auth_headers)
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["content"] == "first message"
    assert messages[1]["content"] == "second message"


def test_get_conversation_marks_messages_as_read(client, verified_user, auth_headers):
    sara_headers = create_verified_user(
        client, "sara", "sara@example.com", "password123"
    )

    # sara sends a message to testuser
    sara_token = get_token(client, "sara")
    with client.websocket_connect(f"/ws/{sara_token}") as ws:
        ws.send_json({"to": "testuser", "content": "hey testuser"})
        ws.receive_json()

    # testuser opens the conversation — messages should be marked as read
    client.get("/conversations/sara", headers=auth_headers)

    # fetch again and check is_read
    response = client.get("/conversations/sara", headers=auth_headers)
    messages = response.json()
    assert messages[0]["is_read"] == True


def test_get_conversation_not_found(client, auth_headers):
    response = client.get("/conversations/nobody", headers=auth_headers)
    assert response.status_code == 404


def test_get_conversations_requires_auth(client):
    response = client.get("/conversations")
    assert response.status_code == 401
