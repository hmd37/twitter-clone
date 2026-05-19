def test_like_tweet(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "like me"}, headers=auth_headers).json()

    response = client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    assert response.status_code == 204

    tweet_response = client.get(f"/tweets/{tweet['id']}", headers=auth_headers).json()
    assert tweet_response["like_count"] == 1
    assert tweet_response["is_liked"] == True


def test_like_tweet_requires_auth(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "like me"}, headers=auth_headers).json()

    response = client.post(f"/tweets/{tweet['id']}/like")
    assert response.status_code == 401


def test_like_tweet_twice(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "like me"}, headers=auth_headers).json()

    client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    response = client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    assert response.status_code == 400


def test_like_tweet_not_found(client, auth_headers):
    response = client.post("/tweets/999/like", headers=auth_headers)
    assert response.status_code == 404


def test_unlike_tweet(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "like me"}, headers=auth_headers).json()

    client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    response = client.delete(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    assert response.status_code == 204

    tweet_response = client.get(f"/tweets/{tweet['id']}").json()
    assert tweet_response["like_count"] == 0
    assert tweet_response["is_liked"] == False


def test_unlike_tweet_not_liked(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "not liked"}, headers=auth_headers).json()

    response = client.delete(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    assert response.status_code == 400


def test_is_liked_false_without_auth(client, auth_headers):
    tweet = client.post("/tweets/", json={"content": "hello"}, headers=auth_headers).json()
    client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)

    # fetch without auth - is_liked should be False
    response = client.get(f"/tweets/{tweet['id']}").json()
    assert response["like_count"] == 1
    assert response["is_liked"] == False


def test_like_count_multiple_users(client, auth_headers):
    from tests.conftest import create_verified_user
    tweet = client.post("/tweets/", json={"content": "popular"}, headers=auth_headers).json()

    user2_headers = create_verified_user(client, "user2", "user2@example.com", "password123")

    client.post(f"/tweets/{tweet['id']}/like", headers=auth_headers)
    client.post(f"/tweets/{tweet['id']}/like", headers=user2_headers)

    response = client.get(f"/tweets/{tweet['id']}").json()
    assert response["like_count"] == 2