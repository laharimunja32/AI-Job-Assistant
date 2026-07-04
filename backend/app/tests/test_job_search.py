from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
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


def _auth_header(email: str = "search@example.com") -> dict[str, str]:
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        from app.core.security import get_password_hash

        user = User(email=email, full_name="Search User", hashed_password=get_password_hash("password123"), is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(subject=user.email, role=user.role)
    db.close()
    return {"Authorization": f"Bearer {token}"}


def test_live_job_search_requires_auth() -> None:
    response = client.post("/api/v1/job-search/search", json={"keyword": "python"})
    assert response.status_code == 401


def test_live_job_search_returns_results() -> None:
    headers = _auth_header()
    response = client.post(
        "/api/v1/job-search/search",
        json={"keyword": "python", "location": "Hyderabad", "remote": True, "page": 1, "size": 10},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["page"] == 1
    job = data["items"][0]
    assert "title" in job
    assert "company" in job
    assert "description_preview" in job
    assert "company_logo" in job


def test_job_search_history() -> None:
    headers = _auth_header("history@example.com")
    client.post("/api/v1/job-search/search", json={"keyword": "python"}, headers=headers)
    response = client.get("/api/v1/job-search/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    detail = client.get(f"/api/v1/job-search/{data['items'][0]['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["keyword"] == "python"
