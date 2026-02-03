def test_get_user_profile_authenticated(client, student_headers):
    response = client.get("/users/me", headers=student_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "student@test.com"
    assert body["role"] == "student"


def test_get_user_profile_requires_auth(client):
    response = client.get("/users/me")
    assert response.status_code == 401
