def test_create_tweet(client, auth_headers):
    response = client.post("/tweets/", json={"content": "hello world"}, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "hello world"
    assert data["author"]["username"] == "testuser"
    assert data["like_count"] == 0
    assert data["is_liked"] == False


def test_create_tweet_requires_auth(client):
    response = client.post("/tweets/", json={"content": "hello"})
    assert response.status_code == 401


def test_create_tweet_too_long(client, auth_headers):
    response = client.post("/tweets/", json={"content": "x" * 281}, headers=auth_headers)
    assert response.status_code == 400


def test_get_tweets_empty(client):
    response = client.get("/tweets/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tweets(client, auth_headers):
    client.post("/tweets/", json={"content": "tweet 1"}, headers=auth_headers)
    client.post("/tweets/", json={"content": "tweet 2"}, headers=auth_headers)

    response = client.get("/tweets/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_tweets_no_auth_works(client, auth_headers):
    client.post("/tweets/", json={"content": "public tweet"}, headers=auth_headers)

    response = client.get("/tweets/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_tweets_order(client, auth_headers):
    client.post("/tweets/", json={"content": "first"}, headers=auth_headers)
    client.post("/tweets/", json={"content": "second"}, headers=auth_headers)

    response = client.get("/tweets/")
    tweets = response.json()
    assert tweets[0]["content"] == "second"
    assert tweets[1]["content"] == "first"


def test_get_single_tweet(client, auth_headers):
    created = client.post("/tweets/", json={"content": "hello"}, headers=auth_headers).json()

    response = client.get(f"/tweets/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_tweet_not_found(client):
    response = client.get("/tweets/999")
    assert response.status_code == 404


def test_delete_tweet(client, auth_headers):
    created = client.post("/tweets/", json={"content": "to delete"}, headers=auth_headers).json()

    response = client.delete(f"/tweets/{created['id']}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/tweets/{created['id']}")
    assert response.status_code == 404


def test_delete_tweet_requires_auth(client, auth_headers):
    created = client.post("/tweets/", json={"content": "hello"}, headers=auth_headers).json()

    response = client.delete(f"/tweets/{created['id']}")
    assert response.status_code == 401


def test_delete_tweet_not_owner(client, auth_headers):
    from tests.conftest import create_verified_user
    user2_headers = create_verified_user(client, "user2", "user2@example.com", "password123")

    created = client.post("/tweets/", json={"content": "mine"}, headers=auth_headers).json()

    response = client.delete(f"/tweets/{created['id']}", headers=user2_headers)
    assert response.status_code == 403
    