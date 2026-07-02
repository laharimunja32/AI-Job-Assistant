from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.job import Job
from app.db.models.user import User
from app.db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed_user_and_job(db):
    user = User(email="apps@example.com", hashed_password="hash", full_name="App User")
    db.add(user)
    db.flush()
    job = Job(
        title="Backend Engineer",
        company_name="Acme",
        description="Build APIs",
        status="active",
        apply_url="https://acme.test/apply",
    )
    db.add(job)
    db.commit()
    db.refresh(user)
    db.refresh(job)
    return user, job


def test_applications_crud_and_history() -> None:
    db = TestingSessionLocal()
    user, job = _seed_user_and_job(db)
    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/applications",
        headers=headers,
        json={
            "job_id": job.id,
            "company_name": "Acme",
            "job_title": "Backend Engineer",
            "apply_url": "https://acme.test/apply",
            "status": "ready_to_apply",
            "priority": 3,
            "tags": ["python"],
        },
    )
    assert created.status_code == 201
    created_payload = created.json()
    application_id = created_payload["id"]

    listed = client.get("/api/v1/applications?status=ready_to_apply", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    updated = client.put(
        f"/api/v1/applications/{application_id}",
        headers=headers,
        json={"status": "applied", "notes": "Submitted today"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "applied"

    favorite = client.patch(f"/api/v1/applications/{application_id}/favorite", headers=headers, json={"is_favorite": True})
    assert favorite.status_code == 200
    assert favorite.json()["is_favorite"] is True

    history = client.get(f"/api/v1/applications/{application_id}/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 2

    deleted = client.delete(f"/api/v1/applications/{application_id}", headers=headers)
    assert deleted.status_code == 204

    post_delete_list = client.get("/api/v1/applications", headers=headers)
    assert post_delete_list.status_code == 200
    assert all(item["id"] != application_id for item in post_delete_list.json()["items"])

    app.dependency_overrides.clear()
    db.close()
