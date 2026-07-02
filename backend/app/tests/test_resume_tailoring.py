from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.db.session import get_db
from app.services import resume_tailoring_service
from app.services.resume_tailoring_service import ResumeTailoringService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed(db):
    user = User(email="tailor@example.com", hashed_password="hash", full_name="Tailor User")
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id, location="Hyderabad", skills=["Python", "FastAPI"], projects=[{"name": "ATS Helper"}]))
    db.add(
        Resume(
            user_id=user.id,
            filename="master_resume.pdf",
            content_type="application/pdf",
            file_size=1024,
            storage_path=str((Path(__file__).resolve().parents[3] / "uploads" / "resumes" / "test_resume.txt")),
            is_active=True,
            file_metadata={"content": "Python FastAPI SQL AWS", "experience_years": 3},
        )
    )
    job = Job(
        title="Backend Engineer",
        company_name="Acme",
        description="Build APIs with Python, FastAPI and SQL. Deliver reliable services.",
        skills=["Python", "FastAPI", "SQL"],
        tags=["AWS", "Docker"],
        experience="2-4 years",
        status="active",
        apply_url="https://example.com/backend",
    )
    db.add(job)
    db.commit()
    db.refresh(user)
    db.refresh(job)
    return user, job


def test_resume_tailoring_generation_flow() -> None:
    db = TestingSessionLocal()
    resume_tailoring_service.SessionLocal = TestingSessionLocal
    app = create_app()
    user, job = _seed(db)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    generate = client.post(f"/api/v1/resume-tailoring/generate/{job.id}", headers=headers)
    assert generate.status_code == 200
    tailored_id = generate.json()["tailored_resume_id"]
    ResumeTailoringService(db=db)._run_generation_task(tailored_id)

    payload = None
    for _ in range(20):
        response = client.get(f"/api/v1/resume-tailoring/{tailored_id}", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] == "completed":
            break
        time.sleep(0.1)

    assert payload is not None
    assert payload["status"] == "completed"
    assert payload["ats_score"] is not None
    assert payload["markdown_content"]

    history = client.get("/api/v1/resume-tailoring/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 1

    download = client.get(f"/api/v1/resume-tailoring/{tailored_id}/download?format=markdown", headers=headers)
    assert download.status_code == 200
    assert b"Tailored Resume" in download.content

    second = client.post(f"/api/v1/resume-tailoring/generate/{job.id}", headers=headers)
    assert second.status_code == 200
    assert second.json()["cached"] is True

    delete_resp = client.delete(f"/api/v1/resume-tailoring/{tailored_id}", headers=headers)
    assert delete_resp.status_code == 204

    app.dependency_overrides.clear()
    db.close()
