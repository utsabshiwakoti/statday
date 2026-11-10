from app.config import settings
from tests.conftest import create_key, signup


def test_signup_login_and_me(client):
    signup(client, "Dev@Example.com")
    assert client.post("/api/auth/signup", json={"email": "dev@example.com", "password": "another-one"}
                       ).status_code == 409
    res = client.post("/api/auth/token", data={"username": "dev@example.com", "password": "correct-horse"})
    assert res.status_code == 200
    auth = {"Authorization": f"Bearer {res.json()['access_token']}"}
    assert client.get("/api/me", headers=auth).json()["email"] == "dev@example.com"

    wrong = client.post("/api/auth/token", data={"username": "dev@example.com", "password": "nope-nope"})
    assert wrong.status_code == 401
    assert client.get("/api/me").status_code == 401


def test_key_is_shown_once_and_stored_hashed(client, session_factory):
    auth = signup(client)
    created = create_key(client, auth)
    assert created["key"].startswith(created["prefix"] + "_")

    listed = client.get("/api/keys", headers=auth).json()
    assert "key" not in listed[0] and listed[0]["prefix"] == created["prefix"]

    from app.models import ApiKey
    with session_factory() as db:
        stored = db.get(ApiKey, created["id"])
        assert created["key"] not in (stored.key_hash, stored.prefix)


def test_usage_is_counted_per_day(client):
    auth = signup(client)
    key = create_key(client, auth)
    for _ in range(3):
        client.get("/v1/regions", headers={"X-API-Key": key["key"]})
    client.get("/v1/regions")  # anonymous: not anyone's usage

    usage = client.get("/api/usage", params={"days": 7}, headers=auth).json()
    assert usage["total"] == 3
    assert usage["days"][-1] == {"day": "2026-11-10", "count": 3}
    assert len(usage["days"]) == 7
    assert usage["by_key"] == {str(key["id"]): 3}
    assert client.get("/api/keys", headers=auth).json()[0]["last_used_at"] is not None


def test_rotate_and_revoke(client):
    auth = signup(client)
    old = create_key(client, auth, "Production")

    rotated = client.post(f"/api/keys/{old['id']}/rotate", headers=auth)
    assert rotated.status_code == 201
    new = rotated.json()
    assert new["name"] == "Production" and new["key"] != old["key"]
    assert client.get("/v1/regions", headers={"X-API-Key": old["key"]}).status_code == 401
    assert client.get("/v1/regions", headers={"X-API-Key": new["key"]}).status_code == 200

    assert client.delete(f"/api/keys/{new['id']}", headers=auth).json()["revoked_at"] is not None
    assert client.get("/v1/regions", headers={"X-API-Key": new["key"]}).status_code == 401
    assert client.post(f"/api/keys/{new['id']}/rotate", headers=auth).status_code == 409


def test_key_limit(client, monkeypatch):
    monkeypatch.setattr(settings, "max_keys_per_developer", 2)
    auth = signup(client)
    first = create_key(client, auth)
    create_key(client, auth)
    assert client.post("/api/keys", json={"name": "third"}, headers=auth).status_code == 409
    client.delete(f"/api/keys/{first['id']}", headers=auth)  # revoked keys don't count
    create_key(client, auth)


def test_developers_cannot_touch_each_others_keys(client):
    alice = signup(client, "alice@example.com")
    bob = signup(client, "bob@example.com")
    key = create_key(client, alice)
    assert client.delete(f"/api/keys/{key['id']}", headers=bob).status_code == 404
    assert client.post(f"/api/keys/{key['id']}/rotate", headers=bob).status_code == 404
    assert client.get("/api/keys", headers=bob).json() == []
    assert client.get("/api/usage", headers=bob).json()["total"] == 0
