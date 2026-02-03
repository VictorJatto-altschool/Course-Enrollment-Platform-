def test_admin_view_all_enrollments(client, admin_token):
    response = client.get(
        "/admin/enrollments",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_student_cannot_view_all_enrollments(client, student_token):
    response = client.get(
        "/admin/enrollments",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403


def test_admin_view_course_enrollments(client, admin_headers, student_headers, create_course):
    course = create_course(title="Admin Course Enrollment View")
    enroll = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert enroll.status_code == 201

    response = client.get(
        f"/admin/courses/{course['id']}/enrollments",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_admin_can_remove_student(client, admin_headers, student_headers, create_course):
    course = create_course(title="Admin Removal Course")
    enroll = client.post(
        f"/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert enroll.status_code == 201

    enrollments = client.get(
        "/admin/enrollments",
        params={"course_id": course["id"]},
        headers=admin_headers,
    )
    assert enrollments.status_code == 200
    enrollment_id = enrollments.json()[0]["id"]

    response = client.delete(
        f"/admin/enrollments/{enrollment_id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
