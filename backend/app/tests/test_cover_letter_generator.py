from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.cover_letter_generator import CoverLetter  # noqa: F401
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.db.session import get_db
from app.services.cover_letter_generator_service import CoverLetterGeneratorService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _seed(db, email: str = "clgen@example.com"):
    user = User(email=email, hashed_password="hash", full_name="CL Gen User")
    db.add(user)
    db.flush()
    db.add(
        Profile(
            user_id=user.id,
            location="Hyderabad",
            skills=["Python", "FastAPI", "SQL", "Docker"],
            education=[{"degree": "B.Tech Computer Science", "institution": "State University"}],
            certifications=[{"name": "AWS Certified Developer"}],
            projects=[{"name": "API Platform", "description": "Built REST APIs with Python and FastAPI"}],
        )
    )
    resume = Resume(
        user_id=user.id,
        filename="master_resume.pdf",
        content_type="application/pdf",
        file_size=1024,
        storage_path=str((Path(__file__).resolve().parents[3] / "uploads" / "resumes" / "test_resume.txt")),
        is_active=True,
        file_metadata={
            "content": "Python developer with 3 years experience. Built REST APIs using FastAPI and SQL. Deployed with Docker on AWS.",
            "experience_years": 3,
        },
    )
    db.add(resume)
    db.commit()
    db.refresh(user)
    db.refresh(resume)
    return user, resume


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(subject=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def _generate_payload(resume_id: int) -> dict:
    return {
        "resume_id": resume_id,
        "job_description": (
            "Backend Engineer at Acme Corp. Requirements: Python, FastAPI, SQL, Docker, AWS. "
            "3+ years experience. Bachelor's degree in Computer Science required."
        ),
        "job_title": "Backend Engineer",
        "company_name": "Acme Corp",
        "template_name": "professional",
        "tone": "professional",
        "length": "medium",
    }


def test_generate_cover_letter():
    db = TestingSessionLocal()
    user, resume = _seed(db)
    headers = _auth_headers(user)
    response = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=_generate_payload(resume.id))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["company_name"] == "Acme Corp"
    assert len(data["generated_letter"]) > 50
    assert "Acme Corp" in data["generated_letter"]
    assert "Haskell" not in data["generated_letter"]
    db.close()


def test_cover_letter_history_and_detail():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="clgen2@example.com")
    headers = _auth_headers(user)
    generated = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=_generate_payload(resume.id))
    assert generated.status_code == 200
    letter_id = generated.json()["id"]

    history = client.get("/api/v1/cover-letter-generator/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 1

    detail = client.get(f"/api/v1/cover-letter-generator/{letter_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == letter_id
    assert detail.json()["template_name"] == "professional"
    db.close()


def test_update_cover_letter():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="clgen3@example.com")
    headers = _auth_headers(user)
    generated = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=_generate_payload(resume.id))
    letter_id = generated.json()["id"]
    updated_text = "Updated cover letter content with sufficient length for validation."
    updated = client.put(
        f"/api/v1/cover-letter-generator/{letter_id}",
        headers=headers,
        json={"generated_letter": updated_text},
    )
    assert updated.status_code == 200
    assert updated.json()["generated_letter"] == updated_text
    db.close()


def test_delete_cover_letter():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="clgen4@example.com")
    headers = _auth_headers(user)
    generated = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=_generate_payload(resume.id))
    letter_id = generated.json()["id"]
    deleted = client.delete(f"/api/v1/cover-letter-generator/{letter_id}", headers=headers)
    assert deleted.status_code == 204
    missing = client.get(f"/api/v1/cover-letter-generator/{letter_id}", headers=headers)
    assert missing.status_code == 404
    db.close()


def test_download_cover_letter():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="clgen5@example.com")
    headers = _auth_headers(user)
    generated = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=_generate_payload(resume.id))
    letter_id = generated.json()["id"]
    pdf = client.get(f"/api/v1/cover-letter-generator/{letter_id}/download?format=pdf", headers=headers)
    assert pdf.status_code == 200
    assert len(pdf.content) > 0
    docx = client.get(f"/api/v1/cover-letter-generator/{letter_id}/download?format=docx", headers=headers)
    assert docx.status_code == 200
    db.close()


def test_generate_requires_authentication():
    db = TestingSessionLocal()
    _, resume = _seed(db, email="clgen6@example.com")
    response = client.post("/api/v1/cover-letter-generator/generate", json=_generate_payload(resume.id))
    assert response.status_code == 401
    db.close()


def test_service_does_not_invent_experience():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="clgen7@example.com")
    service = CoverLetterGeneratorService(db)
    result = service.generate(
        user,
        resume.id,
        "Looking for expert in Rust, Haskell, and Erlang with 10 years experience.",
        "Systems Engineer",
        "TechCo",
    )
    letter = result["generated_letter"].lower()
    assert "haskell" not in letter
    assert "erlang" not in letter
    assert "rust" not in letter or "rust" in resume.file_metadata["content"].lower()
    db.close()


def test_generate_missing_resume():
    db = TestingSessionLocal()
    user, _ = _seed(db, email="clgen8@example.com")
    headers = _auth_headers(user)
    payload = _generate_payload(99999)
    response = client.post("/api/v1/cover-letter-generator/generate", headers=headers, json=payload)
    assert response.status_code == 404
    db.close()
