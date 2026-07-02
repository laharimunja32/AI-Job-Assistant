from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.application import Application
from app.db.models.job import Job
from app.db.models.user import User
from app.db.session import get_db

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed(db, email: str):
    user = User(email=email, hashed_password="hash", full_name="Monitor User")
    db.add(user)
    db.flush()
    job = Job(title="Backend Engineer", company_name="Acme", status="active")
    db.add(job)
    db.flush()
    app = Application(user_id=user.id, job_id=job.id, company_name="Acme", job_title="Backend Engineer", status="applied")
    db.add(app)
    db.commit()
    db.refresh(user)
    db.refresh(app)
    return user, app


def test_process_email_requires_authorization() -> None:
    db = TestingSessionLocal()
    user, _ = _seed(db, email="monitor-auth@example.com")
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    token = create_access_token(subject=user.email, role=user.role)

    response = client.post(
        "/api/v1/emails/process",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "provider": "gmail",
            "authorization_confirmed": False,
            "sender": "hr@acme.com",
            "subject": "Interview invitation at Acme",
            "body": "Please join: https://meet.google.com/abc",
            "received_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 400
    assert "authorization" in response.json()["detail"].lower()


def test_recruitment_endpoints_flow() -> None:
    db = TestingSessionLocal()
    user, app_obj = _seed(db, email="monitor-flow@example.com")
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    token = create_access_token(subject=user.email, role=user.role)
    headers = {"Authorization": f"Bearer {token}"}

    process_response = client.post(
        "/api/v1/emails/process",
        headers=headers,
        json={
            "provider": "gmail",
            "authorization_confirmed": True,
            "sender": "hr@acme.com",
            "subject": "Online assessment for the role of Backend Engineer",
            "body": "Complete by deadline: 2030-01-01",
            "received_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert process_response.status_code == 201

    assessment_response = client.post(
        "/api/v1/assessments",
        headers=headers,
        json={"application_id": app_obj.id, "assessment_type": "Coding Test", "status": "Pending"},
    )
    assert assessment_response.status_code == 201

    interview_response = client.post(
        "/api/v1/interviews",
        headers=headers,
        json={"application_id": app_obj.id, "interview_type": "Technical", "status": "Scheduled"},
    )
    assert interview_response.status_code == 201

    reminder_response = client.post(
        "/api/v1/reminders",
        headers=headers,
        json={"application_id": app_obj.id, "title": "Prepare coding notes", "due_at": datetime.now(timezone.utc).isoformat()},
    )
    assert reminder_response.status_code == 201

    timeline_response = client.get(f"/api/v1/timeline/{app_obj.id}", headers=headers)
    assert timeline_response.status_code == 200
    assert timeline_response.json()["total"] >= 1

    notifications_response = client.get("/api/v1/notifications/history", headers=headers)
    assert notifications_response.status_code == 200
    assert notifications_response.json()["total"] >= 1
