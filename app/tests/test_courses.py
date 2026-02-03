def test_create_course_admin(client, admin_token):
    response = client.post(
        "/courses",
        json={
            "title": "Physics",
            "code": "PHY101",
            "capacity": 50
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201


def test_list_courses_public(client, create_course):
    course = create_course(title="Listable Course")

    response = client.get("/courses")
    assert response.status_code == 200
    codes = [c.get("code") for c in response.json()]
    assert course["code"] in codes


def test_student_cannot_create_course(client, student_token):
    response = client.post(
        "/courses",
        json={
            "title": "Chemistry",
            "code": "CHE101",
            "capacity": 30
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403


def test_admin_can_delete_course(client, admin_headers, create_course):
    course = create_course(title="Deletable Course")

    response = client.delete(
        f"/courses/{course['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 200

    # Deleted courses should not appear in default listings.
    after = client.get("/courses", params={"code": course["code"]})
    assert after.status_code == 200
    assert after.json() == []


def test_get_course_by_id_public(client, create_course):
    course = create_course(title="By ID Course")
    response = client.get(f"/courses/{course['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == course["id"]


def test_course_code_must_be_unique(client, admin_headers):
    first = client.post(
        "/courses",
        json={"title": "C1", "code": "UNIQ101", "capacity": 10},
        headers=admin_headers,
    )
    assert first.status_code == 201

    second = client.post(
        "/courses",
        json={"title": "C2", "code": "UNIQ101", "capacity": 10},
        headers=admin_headers,
    )
    assert second.status_code == 400


def test_course_capacity_must_be_greater_than_zero(client, admin_headers):
    response = client.post(
        "/courses",
        json={"title": "Bad", "code": "BADCAP", "capacity": 0},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_admin_can_update_course_details(client, admin_headers, create_course):
    course = create_course(title="Updatable", capacity=20)
    response = client.patch(
        f"/courses/{course['id']}",
        json={"title": "Updated Title", "capacity": 25},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["capacity"] == 25


def test_admin_can_activate_deactivate_course(client, admin_headers, create_course):
    course = create_course(title="Toggle", is_active=True)

    deactivate = client.patch(
        f"/courses/{course['id']}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    # Public GET by id should now hide inactive courses
    public_get = client.get(f"/courses/{course['id']}")
    assert public_get.status_code == 404
