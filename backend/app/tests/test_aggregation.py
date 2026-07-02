from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.aggregation import AggregationRun
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.user import User
from app.db.models.walk_in import WalkInEvent
from app.services.dashboard.aggregation_service import AggregationService
from app.services.jobs.providers.sample_provider import SampleJobProvider
from app.services.jobs.providers.walkin_provider import SampleWalkInProvider
from app.services.jobs.search_service import JobSearchService
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


def _build_service(db) -> AggregationService:
    job_providers = [SampleJobProvider()]
    walk_in_providers = [SampleWalkInProvider()]
    return AggregationService(
        db=db,
        job_providers=job_providers,
        walk_in_providers=walk_in_providers,
        job_service=JobSearchService(db=db, providers=job_providers),
        walk_in_service=WalkInEventService(db=db, providers=walk_in_providers),
    )


def test_full_aggregation_collects_jobs_and_walk_ins() -> None:
    db = TestingSessionLocal()
    try:
        service = _build_service(db)
        stats = service.run_full_aggregation()

        assert stats["providers_attempted"] >= 1
        assert db.query(Job).count() >= 1
        assert db.query(WalkInEvent).count() >= 1
        assert db.query(AggregationRun).count() == 1
        run = db.query(AggregationRun).first()
        assert run.status in {"success", "partial"}
        assert run.run_type == "full"
    finally:
        db.close()


def test_aggregation_derives_search_terms_from_profiles() -> None:
    db = TestingSessionLocal()
    try:
        user = User(email="agg@example.com", hashed_password="hash", full_name="Agg User")
        db.add(user)
        db.flush()
        profile = Profile(
            user_id=user.id,
            skills=["Python", "FastAPI"],
            preferred_job_roles=["Backend Engineer"],
            preferred_locations=["Hyderabad"],
        )
        db.add(profile)
        db.commit()

        service = _build_service(db)
        keywords, locations = service._derive_search_terms()

        assert "backend engineer" in keywords
        assert "python" in keywords
        assert "Hyderabad" in locations
    finally:
        db.close()


def test_aggregation_history_is_recorded() -> None:
    db = TestingSessionLocal()
    try:
        service = _build_service(db)
        service.run_full_aggregation()
        history = service.get_aggregation_history()

        assert history["total"] >= 1
        assert history["items"][0]["run_type"] == "full"
    finally:
        db.close()


def test_mark_expired_jobs_updates_stale_entries() -> None:
    db = TestingSessionLocal()
    try:
        from datetime import datetime, timedelta

        job = Job(
            title="Old Job",
            company_name="OldCo",
            status="active",
            updated_at=datetime.utcnow() - timedelta(days=45),
        )
        db.add(job)
        db.commit()

        service = _build_service(db)
        expired_count = service.mark_expired_jobs(days=30)

        db.refresh(job)
        assert expired_count >= 1
        assert job.status == "expired"
    finally:
        db.close()
