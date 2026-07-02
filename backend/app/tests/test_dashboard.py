from __future__ import annotations

from datetime import date, datetime, timedelta

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
from app.db.models.walk_in import WalkInEvent
from app.db.session import get_db
from app.services.dashboard.cache import DashboardCache
from app.services.dashboard.dashboard_service import DashboardService
from app.services.dashboard.notification_prep_service import NotificationPrepService
from app.services.jobs.match_service import JobMatchService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed_user_with_data(db, email: str = "dash@example.com") -> User:
    user = User(email=email, hashed_password="hash", full_name="Dash User")
    db.add(user)
    db.flush()

    profile = Profile(
        user_id=user.id,
        location="Hyderabad",
        skills=["Python", "FastAPI"],
        preferred_job_roles=["Backend Engineer"],
        preferred_locations=["Hyderabad", "Remote"],
        education=[{"degree": "B.Tech"}],
        certifications=[{"name": "AWS"}],
    )
    db.add(profile)

    resume = Resume(
        user_id=user.id,
        filename="resume.pdf",
        content_type="application/pdf",
        file_size=1000,
        storage_path="/tmp/resume.pdf",
        is_active=True,
        file_metadata={"experience_years": 2},
    )
    db.add(resume)

    job = Job(
        title="Python Backend Engineer",
        company_name="Example Labs",
        description="Build APIs",
        skills=["Python", "FastAPI"],
        experience="0-2 years",
        work_mode="Remote",
        location="Hyderabad",
        employment_type="Full Time",
        status="active",
        apply_url=f"https://example.com/jobs/{email}",
    )
    db.add(job)

    walk_in = WalkInEvent(
        company_name="TCS",
        job_role="Software Engineer",
        city="Hyderabad",
        walk_in_date=date.today() + timedelta(days=1),
        event_status="Upcoming",
        skills=["Python"],
    )
    db.add(walk_in)
    db.commit()
    db.refresh(user)
    return user


def test_dashboard_service_returns_personalized_sections() -> None:
    db = TestingSessionLocal()
    try:
        user = _seed_user_with_data(db, email="dash1@example.com")
        service = DashboardService(db=db, cache=DashboardCache(ttl_seconds=60))

        dashboard = service.get_full_dashboard(user, size=5)

        assert "statistics" in dashboard
        assert dashboard["statistics"]["total_active_jobs"] >= 1
        assert dashboard["profile_summary"]["has_profile"] is True
        assert dashboard["new_jobs"]["total"] >= 0
        assert dashboard["remote_jobs"]["total"] >= 1
    finally:
        db.close()


def test_dashboard_high_matches_filters_by_score() -> None:
    db = TestingSessionLocal()
    try:
        user = _seed_user_with_data(db, email="dash2@example.com")
        match_service = JobMatchService(db=db)
        match_service.match_all_jobs(user)

        service = DashboardService(db=db)
        high_matches = service.get_high_match_jobs(user, min_score=0)

        assert high_matches["total"] >= 1
        assert high_matches["items"][0]["match_score"] is not None
    finally:
        db.close()


def test_notification_prep_identifies_candidates() -> None:
    db = TestingSessionLocal()
    try:
        user = _seed_user_with_data(db, email="dash3@example.com")
        match_service = JobMatchService(db=db)
        match_service.match_all_jobs(user)

        service = NotificationPrepService(db=db)
        candidates = service.identify_candidates(user)

        assert "newly_matched_jobs" in candidates
        assert "newly_added_walk_ins" in candidates
        assert "high_priority_opportunities" in candidates
        assert "jobs_closing_soon" in candidates
    finally:
        db.close()


def test_dashboard_api_requires_auth() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 401


def test_dashboard_api_returns_data_for_authenticated_user() -> None:
    db = TestingSessionLocal()
    user = _seed_user_with_data(db, email="dash4@example.com")

    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)

    response = client.get("/api/v1/dashboard/statistics", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_active_jobs" in data
    assert "profile_completeness" in data
    assert "forms_detected" in data
    assert "average_fill_success_rate" in data

    response = client.get("/api/v1/dashboard/recommended", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "items" in response.json()

    response = client.post("/api/v1/dashboard/refresh", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["matches_computed"] >= 1

    app.dependency_overrides.clear()
