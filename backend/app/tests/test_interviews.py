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
from app.db.models.interview import InterviewPreparation  # noqa: F401  Import for model registration
from app.services.interview_service import InterviewService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed(db, email: str = "interview@example.com"):
    user = User(email=email, hashed_password="hash", full_name="Interview User")
    db.add(user)
    db.flush()
    db.add(
        Profile(
            user_id=user.id,
            location="Hyderabad",
            skills=["Python", "FastAPI", "SQL"],
            projects=[{"name": "ATS Helper"}],
        )
    )
    db.add(
        Resume(
            user_id=user.id,
            filename="master_resume.pdf",
            content_type="application/pdf",
            file_size=1024,
            storage_path=str((Path(__file__).resolve().parents[3] / "uploads" / "resumes" / "test_resume.txt")),
            is_active=True,
            file_metadata={"content": "Python FastAPI SQL AWS backend APIs", "experience_years": 3},
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


def _complete_preparation(client, headers, job_id: int, db) -> int:
    generate = client.post(f"/api/v1/interviews/generate/{job_id}", headers=headers)
    assert generate.status_code == 200
    preparation_id = generate.json()["preparation_id"]

    db.commit()
    InterviewService(db=db)._execute_generation(db, preparation_id)
    db.expire_all()

    payload = None
    for _ in range(20):
        response = client.get(f"/api/v1/interviews/{preparation_id}", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] == "completed":
            break
        time.sleep(0.1)

    assert payload is not None
    assert payload["status"] == "completed"
    assert payload["questions"]
    return preparation_id


def test_interview_generation_history_and_cache() -> None:
    db = TestingSessionLocal()
    app = create_app()
    user, job = _seed(db, email="interview-cache@example.com")

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    preparation_id = _complete_preparation(client, headers, job.id, db)
    assert preparation_id > 0

    history = client.get("/api/v1/interviews/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 0

    second = client.post(f"/api/v1/interviews/generate/{job.id}", headers=headers)
    assert second.status_code == 200
    assert second.json()["cached"] is True

    delete_resp = client.delete(f"/api/v1/interviews/{preparation_id}", headers=headers)
    assert delete_resp.status_code == 204

    app.dependency_overrides.clear()
    db.close()


def test_interview_session_answer_feedback_statistics() -> None:
    db = TestingSessionLocal()
    app = create_app()
    user, job = _seed(db, email="interview-session@example.com")

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    preparation_id = _complete_preparation(client, headers, job.id, db)

    start = client.post(f"/api/v1/interviews/{preparation_id}/start", headers=headers)
    assert start.status_code == 200
    start_payload = start.json()
    assert start_payload["current_question"]["question_text"]

    detail = client.get(f"/api/v1/interviews/{preparation_id}", headers=headers)
    question_count = len(detail.json()["questions"])

    for index in range(question_count):
        answer = client.post(
            f"/api/v1/interviews/{preparation_id}/answer",
            headers=headers,
            json={
                "answer_text": f"My structured answer for question {index + 1} because it delivered measurable results.",
                "time_spent_seconds": 90,
            },
        )
        assert answer.status_code == 200
        assert answer.json()["answer"]["ai_score"] is not None

    finish = client.post(f"/api/v1/interviews/{preparation_id}/finish", headers=headers)
    assert finish.status_code == 200
    finish_payload = finish.json()
    assert finish_payload["feedback"]["overall_score"] is not None

    feedback = client.get(f"/api/v1/interviews/{preparation_id}/feedback", headers=headers)
    assert feedback.status_code == 200
    assert feedback.json()["readiness_score"] is not None

    stats = client.get("/api/v1/interviews/statistics", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["practice_sessions"] >= 1
    assert stats.json()["questions_answered"] >= question_count

    app.dependency_overrides.clear()
    db.close()
