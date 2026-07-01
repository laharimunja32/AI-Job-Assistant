from __future__ import annotations

from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.jobs.search_service import JobSearchService


class SearchScheduler:
    """Wrap APScheduler so searches can be triggered on a cadence."""

    def __init__(self, service: JobSearchService):
        self.service = service
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
        self.service.search_jobs(keyword=keyword, location=location, filters=filters)
