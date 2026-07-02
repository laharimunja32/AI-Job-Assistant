from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.db.base import Base
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.db.models.walk_in import WalkInEvent
from app.services.jobs.match_service import JobMatchService
from app.services.jobs.providers.walkin_provider import SampleWalkInProvider
from app.services.jobs.walk_in_duplicate_detection_service import WalkInDuplicateDetectionService
from app.services.jobs.walk_in_parser_service import WalkInParserService
from app.services.jobs.walk_in_service import WalkInEventService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def test_walk_in_parser_normalizes_payload() -> None:
    parser = WalkInParserService()
    payload = {
        "company": "TCS",
        "title": "Software Engineer",
        "description": "Walk-in for backend engineers",
        "venue": "HITECH City",
        "city": "Hyderabad",
        "state": "Telangana",
        "date": "2026-07-10",
        "time": "10:00 AM",
        "deadline": "2026-07-09",
        "skills": "Python, FastAPI",
        "documents_required": "Resume, ID",
        "apply_url": "https://example.com/walkins/tcs",
    }

    result = parser.parse_walk_in_payload(payload)

    assert result["company_name"] == "TCS"
    assert result["job_role"] == "Software Engineer"
    assert result["skills"] == ["Python", "FastAPI"]
    assert result["documents_required"] == ["Resume", "ID"]
    assert result["registration_url"] == "https://example.com/walkins/tcs"


def test_walk_in_duplicate_detection_identifies_matching_events() -> None:
    detector = WalkInDuplicateDetectionService()
    existing_event = WalkInEvent(
        company_name="TCS",
        job_role="Software Engineer",
        city="Hyderabad",
        walk_in_date=date(2026, 7, 10),
        registration_url="https://example.com/walkins/tcs",
    )

    candidate = {
        "company_name": "TCS",
        "job_role": "Software Engineer",
        "city": "Hyderabad",
        "walk_in_date": date(2026, 7, 10),
        "registration_url": "https://example.com/walkins/tcs",
    }

    assert detector.is_duplicate(existing_event, candidate) is True


def test_walk_in_service_refreshes_and_filters_events() -> None:
    db = TestingSessionLocal()
    service = WalkInEventService(
        db=db,
        providers=[SampleWalkInProvider()],
    )

    result = service.refresh_walk_ins()

    assert result["created"] >= 1
    assert result["updated"] >= 0
    assert result["total"] >= 1

    upcoming = service.get_upcoming_walk_ins(page=1, size=10)
    assert upcoming["total"] >= 1

    city_results = service.search_walk_ins(city="Hyderabad")
    assert city_results["total"] >= 1

    company_results = service.search_walk_ins(company="TCS")
    assert company_results["total"] >= 1

    role_results = service.search_walk_ins(role="Data Analyst")
    assert role_results["total"] >= 1

    db.close()


def test_walk_in_service_syncs_events_to_job_records() -> None:
    db = TestingSessionLocal()
    service = WalkInEventService(
        db=db,
        providers=[SampleWalkInProvider()],
    )

    service.refresh_walk_ins()

    job = db.query(Job).filter(Job.title.ilike("%Software%")).first()
    assert job is not None
    assert job.company_name == "TCS"
    assert job.external_id.startswith("walkin:")

    db.close()


def test_walk_in_service_marks_expired_events_completed() -> None:
    db = TestingSessionLocal()
    service = WalkInEventService(db=db, providers=[SampleWalkInProvider()])

    event = WalkInEvent(
        company_name="Legacy Corp",
        job_role="QA Engineer",
        city="Hyderabad",
        walk_in_date=date.today() - timedelta(days=5),
        event_status="Upcoming",
    )
    db.add(event)
    db.commit()

    cleaned = service.cleanup_expired_events()
    db.refresh(event)

    assert cleaned >= 1
    assert event.event_status == "Completed"

    db.close()


def test_walk_in_synced_jobs_can_be_matched() -> None:
    db = TestingSessionLocal()
    try:
        service = WalkInEventService(db=db, providers=[SampleWalkInProvider()])
        service.refresh_walk_ins()

        user = User(email="walkin-matcher@example.com", hashed_password="hash", full_name="Walkin User")
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            location="Hyderabad",
            skills=["Python", "FastAPI", "SQL"],
            certifications=[],
            projects=[],
            education=[{"degree": "B.Tech", "field": "CSE"}],
            preferred_locations=["Hyderabad"],
            work_preferences={"remote": False, "relocation": True},
        )
        db.add(profile)

        resume = Resume(
            user_id=user.id,
            filename="resume.pdf",
            content_type="application/pdf",
            file_size=1000,
            storage_path="/tmp/resume.pdf",
            is_active=True,
            file_metadata={"experience_years": 1},
        )
        db.add(resume)
        db.commit()

        job = db.query(Job).filter(Job.company_name == "TCS").first()
        assert job is not None

        match = JobMatchService(db=db).match_job(job.id, user)
        assert 0 <= match.score <= 100
        assert "Python" in match.matched_skills
    finally:
        db.close()


def test_walk_in_api_endpoints() -> None:
    app = create_app()
    with TestClient(app) as client:
        refresh = client.post("/api/v1/walk-ins/refresh")
        assert refresh.status_code == 200
        assert refresh.json()["total"] >= 1

        all_events = client.get("/api/v1/walk-ins")
        assert all_events.status_code == 200
        assert all_events.json()["total"] >= 1

        today_events = client.get("/api/v1/walk-ins/today")
        assert today_events.status_code == 200

        upcoming_events = client.get("/api/v1/walk-ins/upcoming")
        assert upcoming_events.status_code == 200
        assert upcoming_events.json()["total"] >= 1

        company_search = client.get("/api/v1/walk-ins", params={"company": "Infosys"})
        assert company_search.status_code == 200
        assert company_search.json()["total"] >= 1

        role_search = client.get("/api/v1/walk-ins", params={"role": "Software"})
        assert role_search.status_code == 200
        assert role_search.json()["total"] >= 1

        city_search = client.get("/api/v1/walk-ins", params={"city": "Hyderabad"})
        assert city_search.status_code == 200
        assert city_search.json()["total"] >= 1

        eligibility_search = client.get("/api/v1/walk-ins", params={"eligibility": "Graduates"})
        assert eligibility_search.status_code == 200
        assert eligibility_search.json()["total"] >= 1
