import io

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.db.base import Base
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def test_profile_crud_and_resume_management_flow() -> None:
    register_payload = {
        "email": "profile@example.com",
        "full_name": "Profile User",
        "password": "strongpassword",
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201

    login_payload = {"email": "profile@example.com", "password": "strongpassword"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    tokens = response.json()
    auth_header = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = client.get("/api/v1/profile", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["skills"] == []

    profile_payload = {
        "full_name": "Updated Profile User",
        "phone": "+1-555-1234",
        "address": "123 Main Street",
        "location": "Remote",
        "education": [{"institution": "Example University", "degree": "BS", "field": "CS"}],
        "skills": ["Python", "FastAPI"],
        "certifications": [{"name": "AWS", "issuer": "Amazon"}],
        "projects": [{"name": "AI Job Assistant", "description": "Open source project"}],
        "work_preferences": {"remote": True, "relocation": False},
        "preferred_job_roles": ["Backend Engineer"],
        "preferred_locations": ["Remote", "Austin"],
        "linkedin_url": "https://linkedin.com/in/example",
        "github_url": "https://github.com/example",
        "portfolio_url": "https://example.dev",
    }
    response = client.put("/api/v1/profile", json=profile_payload, headers=auth_header)
    assert response.status_code == 200
    payload = response.json()
    assert payload["full_name"] == "Updated Profile User"
    assert payload["phone"] == "+1-555-1234"
    assert payload["skills"] == ["Python", "FastAPI"]

    resume_bytes = b"%PDF-1.4\n%test pdf data"
    response = client.post(
        "/api/v1/resumes",
        files={"file": ("master_resume.pdf", resume_bytes, "application/pdf")},
        headers=auth_header,
    )
    assert response.status_code == 201
    created_resume = response.json()
    assert created_resume["filename"].endswith(".pdf")
    assert created_resume["is_active"] is True

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("master_resume.pdf", resume_bytes, "application/pdf")},
        headers=auth_header,
    )
    assert response.status_code == 409

    response = client.get("/api/v1/resumes", headers=auth_header)
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == 1
    assert result["items"][0]["filename"].endswith(".pdf")

    response = client.get(f"/api/v1/resumes/{created_resume['id']}/download", headers=auth_header)
    assert response.status_code == 200
    assert response.content == resume_bytes

    response = client.delete(f"/api/v1/resumes/{created_resume['id']}", headers=auth_header)
    assert response.status_code == 204

    response = client.delete("/api/v1/profile", headers=auth_header)
    assert response.status_code == 204
