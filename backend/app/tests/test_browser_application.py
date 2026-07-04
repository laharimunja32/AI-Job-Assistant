from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.models.job import Job
from app.db.models.user import User
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


def _seed_job() -> int:
    db = TestingSessionLocal()
    job = Job(
        title="Automation Test Role",
        company_name="Auto Corp",
        apply_url="https://example.com/apply",
        source_name="test",
        status="active",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()
    return job_id


def _auth_header(email: str = "browser@example.com") -> dict[str, str]:
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, full_name="Browser User", hashed_password=get_password_hash("password123"), is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(subject=user.email, role=user.role)
    db.close()
    return {"Authorization": f"Bearer {token}"}


def test_browser_application_start_and_submit() -> None:
    headers = _auth_header()
    job_id = _seed_job()
    start_response = client.post(
        "/api/v1/browser-application/start",
        json={
            "job_id": job_id,
            "job_title": "Automation Test Role",
            "company_name": "Auto Corp",
            "apply_url": "https://example.com/apply",
        },
        headers=headers,
    )
    assert start_response.status_code == 201
    record = start_response.json()
    assert record["status"] in {"started", "manual_required", "failed"}
    assert record["company_name"] == "Auto Corp"

    detail = client.get(f"/api/v1/browser-application/{record['id']}", headers=headers)
    assert detail.status_code == 200

    history = client.get("/api/v1/browser-application/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 1

    submit = client.post(
        f"/api/v1/browser-application/{record['id']}/submit",
        json={"confirm": True},
        headers=headers,
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "completed"
    assert submit.json()["applied_date"] is not None


def test_browser_application_requires_auth() -> None:
    response = client.get("/api/v1/browser-application/history")
    assert response.status_code == 401
