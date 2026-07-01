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


def test_register_login_and_profile_flow() -> None:
    user_payload = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "strongpassword",
    }

    response = client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert response.json()["is_active"] is True

    login_payload = {"email": "test@example.com", "password": "strongpassword"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    auth_header = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/v1/profile", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    update_payload = {"full_name": "Updated User"}
    response = client.put("/api/v1/profile", json=update_payload, headers=auth_header)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated User"

    refresh_payload = {"refresh_token": tokens["refresh_token"]}
    response = client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert response.status_code == 200
    refreshed = response.json()
    assert refreshed["token_type"] == "bearer"
    assert refreshed["access_token"] != tokens["access_token"]

    response = client.post("/api/v1/auth/logout", json=refresh_payload)
    assert response.status_code == 204

    response = client.post("/api/v1/auth/refresh", json=refresh_payload)
    assert response.status_code == 401
