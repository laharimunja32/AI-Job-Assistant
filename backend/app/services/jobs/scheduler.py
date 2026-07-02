from __future__ import annotations

import logging
from typing import Any, Callable

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.dashboard.aggregation_service import AggregationService
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.sample_provider import SampleJobProvider
from app.services.jobs.providers.walkin_provider import SampleWalkInProvider
from app.services.jobs.search_service import JobSearchService
from app.services.jobs.walk_in_duplicate_detection_service import WalkInDuplicateDetectionService
from app.services.jobs.walk_in_parser_service import WalkInParserService
from app.services.jobs.walk_in_service import WalkInEventService

logger = logging.getLogger(__name__)


def _build_aggregation_service(db) -> AggregationService:
    job_providers = [SampleJobProvider()]
    walk_in_providers = [SampleWalkInProvider()]
    return AggregationService(
        db=db,
        job_providers=job_providers,
        walk_in_providers=walk_in_providers,
        job_service=JobSearchService(
            db=db,
            providers=job_providers,
            parser=JobParserService(),
            duplicate_detector=DuplicateDetectionService(),
        ),
        walk_in_service=WalkInEventService(
            db=db,
            providers=walk_in_providers,
            parser=WalkInParserService(),
            duplicate_detector=WalkInDuplicateDetectionService(),
        ),
    )


class SearchScheduler:
    """Wrap APScheduler so job searches can be triggered on a cadence."""

    def __init__(self, service_factory: Callable[[], JobSearchService] | None = None):
        self._service_factory = service_factory
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def add_search_job(self, job_id: str, interval_minutes: int, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> None:
        self.scheduler.add_job(
            self._run_search,
            "interval",
            minutes=interval_minutes,
            id=job_id,
            args=[keyword, location, filters],
        )

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    def _run_search(self, keyword: str | None, location: str | None, filters: dict[str, Any] | None) -> None:
        db = SessionLocal()
        try:
            if self._service_factory:
                service = self._service_factory()
            else:
                service = JobSearchService(db=db, providers=[SampleJobProvider()])
            service.search_jobs(keyword=keyword, location=location, filters=filters)
        except Exception:
            logger.exception("Scheduled job search failed")
        finally:
            db.close()


class WalkInScheduler:
    """Wrap APScheduler so walk-in discovery can be triggered on a cadence."""

    def __init__(self, service_factory: Callable[[], WalkInEventService] | None = None):
        self._service_factory = service_factory
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def add_refresh_job(self, job_id: str, interval_minutes: int, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> None:
        self.scheduler.add_job(
            self._run_refresh,
            "interval",
            minutes=interval_minutes,
            id=job_id,
            args=[keyword, location, filters],
        )

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    def _run_refresh(self, keyword: str | None, location: str | None, filters: dict[str, Any] | None) -> None:
        db = SessionLocal()
        try:
            if self._service_factory:
                service = self._service_factory()
            else:
                service = WalkInEventService(db=db, providers=[SampleWalkInProvider()])
            service.refresh_walk_ins(keyword=keyword, location=location, filters=filters)
        except Exception:
            logger.exception("Scheduled walk-in refresh failed")
        finally:
            db.close()


class AggregationScheduler:
    """Unified scheduler for job aggregation, walk-in refresh, and dashboard cache invalidation."""

    def __init__(self, on_dashboard_refresh: Callable[[], None] | None = None):
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self._on_dashboard_refresh = on_dashboard_refresh

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def add_job_aggregation(self, job_id: str, interval_minutes: int) -> None:
        self.scheduler.add_job(self._run_job_aggregation, "interval", minutes=interval_minutes, id=job_id)

    def add_walk_in_refresh(self, job_id: str, interval_minutes: int) -> None:
        self.scheduler.add_job(self._run_walk_in_refresh, "interval", minutes=interval_minutes, id=job_id)

    def add_dashboard_refresh(self, job_id: str, interval_minutes: int) -> None:
        self.scheduler.add_job(self._run_dashboard_refresh, "interval", minutes=interval_minutes, id=job_id)

    def add_full_aggregation(self, job_id: str, interval_minutes: int) -> None:
        self.scheduler.add_job(self._run_full_aggregation, "interval", minutes=interval_minutes, id=job_id)

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)

    def _run_job_aggregation(self) -> None:
        db = SessionLocal()
        try:
            service = _build_aggregation_service(db)
            service.aggregate_jobs()
            service.mark_expired_jobs()
        except Exception:
            logger.exception("Scheduled job aggregation failed")
        finally:
            db.close()

    def _run_walk_in_refresh(self) -> None:
        db = SessionLocal()
        try:
            service = _build_aggregation_service(db)
            service.aggregate_walk_ins()
        except Exception:
            logger.exception("Scheduled walk-in refresh failed")
        finally:
            db.close()

    def _run_full_aggregation(self) -> None:
        db = SessionLocal()
        try:
            service = _build_aggregation_service(db)
            service.run_full_aggregation()
        except Exception:
            logger.exception("Scheduled full aggregation failed")
        finally:
            db.close()

    def _run_dashboard_refresh(self) -> None:
        try:
            if self._on_dashboard_refresh:
                self._on_dashboard_refresh()
        except Exception:
            logger.exception("Scheduled dashboard cache refresh failed")
