from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
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


def _auth_header(email: str = "saved@example.com") -> dict[str, str]:
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, full_name="Saved User", hashed_password=get_password_hash("password123"), is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(subject=user.email, role=user.role)
    db.close()
    return {"Authorization": f"Bearer {token}"}


def test_saved_jobs_flow() -> None:
    headers = _auth_header()
    payload = {
        "job_title": "Python Engineer",
        "company_name": "Example Labs",
        "location": "Hyderabad",
        "skills": ["Python", "FastAPI"],
        "job_url": "https://example.com/jobs/1",
    }
    save_response = client.post("/api/v1/saved-jobs", json=payload, headers=headers)
    assert save_response.status_code == 201
    saved = save_response.json()
    assert saved["job_title"] == "Python Engineer"
    assert saved["is_saved"] is True

    list_response = client.get("/api/v1/saved-jobs", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    status_response = client.get("/api/v1/saved-jobs/status/check", params={"saved_job_id": saved["id"]}, headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["is_saved"] is True

    delete_response = client.delete(f"/api/v1/saved-jobs/{saved['id']}", headers=headers)
    assert delete_response.status_code == 204

    list_after = client.get("/api/v1/saved-jobs", headers=headers)
    assert list_after.json()["total"] == 0


def test_saved_jobs_requires_auth() -> None:
    response = client.get("/api/v1/saved-jobs")
    assert response.status_code == 401
