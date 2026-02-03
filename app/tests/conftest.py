import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv(".env.test")
load_dotenv(".env")

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. Create a local .env.test file (not committed) or set it in your shell. "
        "Example: postgresql://postgres:<password>@localhost:5432/course_enrollment_test"
    )

if TEST_DATABASE_URL.startswith("sqlite"):
    raise RuntimeError(
        "TEST_DATABASE_URL points to SQLite, but this project is configured to run tests against PostgreSQL. "
        "Update TEST_DATABASE_URL to a PostgreSQL connection string."
    )

# Ensure app code that expects DATABASE_URL can still run under tests.
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Recreate tables for a clean test database each run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def create_course(client, admin_headers):
    """Create a course via the API and return the JSON response.

    Uses a unique course code by default so tests can run in any order.
    """

    def _create_course(
        *,
        title: str = "Test Course",
        code: str | None = None,
        capacity: int = 50,
        is_active: bool | None = None,
    ):
        if code is None:
            code = f"TST{uuid4().hex[:8].upper()}"

        payload = {
            "title": title,
            "code": code,
            "capacity": capacity,
        }
        if is_active is not None:
            payload["is_active"] = is_active

        response = client.post(
            "/courses",
            json=payload,
            headers=admin_headers,
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _create_course

@pytest.fixture
def student_token(client):
    client.post("/auth/register", json={
        "name": "Student",
        "email": "student@test.com",
        "password": "pass123",
        "role": "student"
    })
    response = client.post(
        "/auth/login",
        json={"email": "student@test.com", "password": "pass123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client):
    client.post("/auth/register", json={
        "name": "Admin",
        "email": "admin@test.com",
        "password": "adminpass",
        "role": "admin"
    })
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "adminpass"},
    )
    return response.json()["access_token"]

