def test_user_registration(client):
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "student"
    })
    assert response.status_code == 201


def test_user_login(client):
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_profile_authenticated(client):
    # Register + login
    register = client.post(
        "/auth/register",
        json={
            "name": "Profile User",
            "email": "profile@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    # Profile endpoint should not require a request body; just the Bearer token.
    me = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    payload = me.json()
    assert payload["email"] == "profile@example.com"


def test_email_must_be_unique(client):
    first = client.post(
        "/auth/register",
        json={
            "name": "User 1",
            "email": "unique@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json={
            "name": "User 2",
            "email": "unique@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert second.status_code == 400


def test_role_must_be_validated(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Bad Role",
            "email": "badrole@example.com",
            "password": "password123",
            "role": "teacher",
        },
    )
    assert response.status_code == 400


def test_inactive_users_cannot_authenticate(client, db_session):
    register = client.post(
        "/auth/register",
        json={
            "name": "Inactive",
            "email": "inactive@example.com",
            "password": "password123",
            "role": "student",
        },
    )
    assert register.status_code == 201

    from app.models.user import User

    user = db_session.query(User).filter(User.email == "inactive@example.com").first()
    assert user is not None
    user.is_active = False
    db_session.commit()

    login = client.post(
        "/auth/login",
        json={"email": "inactive@example.com", "password": "password123"},
    )
    assert login.status_code == 401
