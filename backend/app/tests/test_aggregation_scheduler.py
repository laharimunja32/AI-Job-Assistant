from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.aggregation import AggregationRun
from app.db.models.job import Job
from app.db.models.walk_in import WalkInEvent
from app.services.jobs.scheduler import AggregationScheduler

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

cache_cleared = False


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _on_dashboard_refresh() -> None:
    global cache_cleared
    cache_cleared = True


def test_aggregation_scheduler_runs_full_aggregation(monkeypatch) -> None:
    monkeypatch.setattr("app.services.jobs.scheduler.SessionLocal", TestingSessionLocal)

    scheduler = AggregationScheduler()
    scheduler.start()
    scheduler.add_full_aggregation(job_id="test-full-aggregation", interval_minutes=60)
    scheduler._run_full_aggregation()
    scheduler.shutdown()

    db = TestingSessionLocal()
    try:
        assert db.query(Job).count() >= 1
        assert db.query(WalkInEvent).count() >= 1
        assert db.query(AggregationRun).count() >= 1
    finally:
        db.close()


def test_aggregation_scheduler_dashboard_refresh_callback() -> None:
    global cache_cleared
    cache_cleared = False

    scheduler = AggregationScheduler(on_dashboard_refresh=_on_dashboard_refresh)
    scheduler._run_dashboard_refresh()

    assert cache_cleared is True
