from conftest import create_user


def test_setup_creates_first_owner_only_once(client):
    res = client.post("/auth/setup", json={"username": "boss", "password": "boss12345"})
    assert res.status_code == 201
    assert res.json()["role"] == "owner"

    res = client.post("/auth/setup", json={"username": "boss2", "password": "boss12345"})
    assert res.status_code == 403


def test_login_with_wrong_password_fails(client):
    create_user("owner", "owner12345", "owner")
    res = client.post("/auth/login", data={"username": "owner", "password": "wrongpass"})
    assert res.status_code == 401


def test_me_returns_logged_in_user(client, staff_headers):
    res = client.get("/auth/me", headers=staff_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "staff"


def test_staff_cannot_create_users(client, staff_headers):
    res = client.post(
        "/auth/users",
        json={"username": "newbie", "password": "newbie12345", "role": "staff"},
        headers=staff_headers,
    )
    assert res.status_code == 403