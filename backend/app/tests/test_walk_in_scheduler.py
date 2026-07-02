from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.walk_in import WalkInEvent
from app.services.jobs.scheduler import WalkInScheduler

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def test_walk_in_scheduler_runs_refresh_job(monkeypatch) -> None:
    monkeypatch.setattr("app.services.jobs.scheduler.SessionLocal", TestingSessionLocal)

    scheduler = WalkInScheduler()
    scheduler.start()
    scheduler.add_refresh_job(job_id="test-walk-in-refresh", interval_minutes=60)
    scheduler._run_refresh(None, None, None)
    scheduler.shutdown()

    db = TestingSessionLocal()
    try:
        assert db.query(WalkInEvent).count() >= 1
    finally:
        db.close()
