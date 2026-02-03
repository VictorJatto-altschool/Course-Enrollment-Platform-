def test_student_can_enroll(client, student_headers, create_course):
    course = create_course(title="Enrollment Course")
    response = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 201


def test_duplicate_enrollment_fails(client, student_headers, create_course):
    course = create_course(title="Duplicate Enrollment Course")
    client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    response = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 400


def test_student_can_deregister(client, student_headers, create_course):
    course = create_course(title="Deregister Course")
    enroll = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert enroll.status_code == 201

    response = client.delete(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 200


def test_enrollment_fails_if_course_inactive(client, student_headers, create_course):
    course = create_course(title="Inactive Course", is_active=False)
    response = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 404


def test_enrollment_fails_if_course_full(client, student_headers, create_course):
    course = create_course(title="Full Course", capacity=1)

    first_user = client.post(
        "/auth/register",
        json={
            "name": "Student2",
            "email": "student2@test.com",
            "password": "Student2Pass123!",
            "role": "student",
        },
    )
    assert first_user.status_code == 201
    token = client.post(
        "/auth/login",
        json={"email": "student2@test.com", "password": "Student2Pass123!"},
    ).json()["access_token"]
    student2_headers = {"Authorization": f"Bearer {token}"}

    first = client.post(f"/enrollments/{course['id']}", headers=student_headers)
    assert first.status_code == 201

    second = client.post(f"/enrollments/{course['id']}", headers=student2_headers)
    assert second.status_code == 400
