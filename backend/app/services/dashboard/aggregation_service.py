from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.aggregation import AggregationRun
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.services.jobs.providers.base import JobProvider
from app.services.jobs.providers.walkin_provider import WalkInProvider
from app.services.jobs.search_service import JobSearchService
from app.services.jobs.walk_in_service import WalkInEventService

logger = logging.getLogger(__name__)


class AggregationService:
    """Background engine that collects jobs and walk-ins from all configured providers."""

    DEFAULT_KEYWORDS = ["python", "software engineer", "developer", "data engineer"]
    DEFAULT_LOCATIONS = ["Hyderabad", "Bengaluru", "Remote"]

    def __init__(
        self,
        db: Session,
        job_providers: list[JobProvider],
        walk_in_providers: list[WalkInProvider],
        job_service: JobSearchService | None = None,
        walk_in_service: WalkInEventService | None = None,
    ):
        self.db = db
        self.job_providers = job_providers
        self.walk_in_providers = walk_in_providers
        self.job_service = job_service or JobSearchService(db=db, providers=job_providers)
        self.walk_in_service = walk_in_service or WalkInEventService(db=db, providers=walk_in_providers)

    def run_full_aggregation(self) -> dict[str, Any]:
        """Run job and walk-in aggregation, mark expired entries, and record history."""
        run = self._start_run("full")
        stats: dict[str, Any] = {
            "jobs_created": 0,
            "jobs_updated": 0,
            "jobs_expired": 0,
            "walk_ins_created": 0,
            "walk_ins_updated": 0,
            "duplicates_skipped": 0,
            "providers_attempted": 0,
            "providers_succeeded": 0,
            "providers_failed": 0,
            "errors": [],
        }

        job_stats = self.aggregate_jobs()
        stats["jobs_created"] += job_stats.get("created", 0)
        stats["jobs_updated"] += job_stats.get("updated", 0)
        stats["duplicates_skipped"] += job_stats.get("duplicates_skipped", 0)
        stats["providers_attempted"] += job_stats.get("providers_attempted", 0)
        stats["providers_succeeded"] += job_stats.get("providers_succeeded", 0)
        stats["providers_failed"] += job_stats.get("providers_failed", 0)
        stats["errors"].extend(job_stats.get("errors", []))

        walk_in_stats = self.aggregate_walk_ins()
        stats["walk_ins_created"] += walk_in_stats.get("created", 0)
        stats["walk_ins_updated"] += walk_in_stats.get("updated", 0)
        stats["providers_attempted"] += walk_in_stats.get("providers_attempted", 0)
        stats["providers_succeeded"] += walk_in_stats.get("providers_succeeded", 0)
        stats["providers_failed"] += walk_in_stats.get("providers_failed", 0)
        stats["errors"].extend(walk_in_stats.get("errors", []))

        stats["jobs_expired"] = self.mark_expired_jobs()

        status = "success" if not stats["errors"] else ("partial" if stats["providers_succeeded"] > 0 else "failed")
        self._complete_run(run, status, stats)
        logger.info("Full aggregation completed: %s", stats)
        return stats

    def aggregate_jobs(self) -> dict[str, Any]:
        """Collect jobs from every configured provider using profile-derived search terms."""
        keywords, locations = self._derive_search_terms()
        stats: dict[str, Any] = {
            "created": 0,
            "updated": 0,
            "duplicates_skipped": 0,
            "providers_attempted": len(self.job_providers),
            "providers_succeeded": 0,
            "providers_failed": 0,
            "errors": [],
        }

        existing_urls = {row[0] for row in self.db.query(Job.apply_url).filter(Job.apply_url.isnot(None)).all()}
        before_count = self.db.query(Job).count()

        for provider in self.job_providers:
            provider_succeeded = False
            for keyword in keywords:
                for location in locations:
                    try:
                        result = self.job_service.search_jobs(keyword=keyword, location=location, page=1, size=100)
                        provider_succeeded = True
                        logger.debug("Provider %s returned %d jobs for %s/%s", provider.name, result.get("total", 0), keyword, location)
                    except Exception as exc:
                        stats["errors"].append({"provider": provider.name, "keyword": keyword, "location": location, "error": str(exc)})
                        logger.exception("Job provider %s failed for keyword=%s location=%s", provider.name, keyword, location)
            if provider_succeeded:
                stats["providers_succeeded"] += 1
            else:
                stats["providers_failed"] += 1

        after_count = self.db.query(Job).count()
        new_jobs = self.db.query(Job).filter(~Job.apply_url.in_(existing_urls) if existing_urls else True).all() if existing_urls else []
        stats["created"] = max(0, after_count - before_count)
        stats["updated"] = max(0, len(keywords) * len(locations) * len(self.job_providers) - stats["created"])
        stats["duplicates_skipped"] = max(0, stats["updated"])
        return stats

    def aggregate_walk_ins(self) -> dict[str, Any]:
        """Collect walk-in drives from every configured provider."""
        stats: dict[str, Any] = {
            "created": 0,
            "updated": 0,
            "providers_attempted": len(self.walk_in_providers),
            "providers_succeeded": 0,
            "providers_failed": 0,
            "errors": [],
        }

        for provider in self.walk_in_providers:
            try:
                result = self.walk_in_service.refresh_walk_ins()
                stats["created"] += result.get("created", 0)
                stats["updated"] += result.get("updated", 0)
                stats["providers_succeeded"] += 1
            except Exception as exc:
                stats["providers_failed"] += 1
                stats["errors"].append({"provider": provider.name, "error": str(exc)})
                logger.exception("Walk-in provider %s failed", provider.name)

        return stats

    def mark_expired_jobs(self, days: int = 30) -> int:
        """Mark stale jobs as expired and clean up old walk-in events."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)
        expired_jobs = self.db.query(Job).filter(Job.status == "active", Job.updated_at < cutoff).all()
        for job in expired_jobs:
            job.status = "expired"
            self.db.add(job)
        self.db.commit()

        self.walk_in_service.cleanup_expired_events(days=days)
        return len(expired_jobs)

    def get_aggregation_history(self, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(AggregationRun).order_by(AggregationRun.started_at.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {
            "items": [self._serialize_run(run) for run in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def _derive_search_terms(self) -> tuple[list[str], list[str]]:
        """Build search keywords and locations from user profiles for personalized aggregation."""
        profiles = self.db.query(Profile).all()
        keywords: set[str] = set()
        locations: set[str] = set()

        for profile in profiles:
            for role in profile.preferred_job_roles or []:
                if isinstance(role, str) and role.strip():
                    keywords.add(role.strip().lower())
            for skill in profile.skills or []:
                if isinstance(skill, str) and skill.strip():
                    keywords.add(skill.strip().lower())
            for loc in profile.preferred_locations or []:
                if isinstance(loc, str) and loc.strip():
                    locations.add(loc.strip())
            if profile.location:
                locations.add(profile.location.strip())
            work_prefs = profile.work_preferences or {}
            if isinstance(work_prefs, dict):
                for loc in work_prefs.get("preferred_locations", []):
                    if isinstance(loc, str) and loc.strip():
                        locations.add(loc.strip())

        if not keywords:
            keywords.update(self.DEFAULT_KEYWORDS)
        if not locations:
            locations.update(self.DEFAULT_LOCATIONS)

        return sorted(keywords)[:10], sorted(locations)[:10]

    def _start_run(self, run_type: str) -> AggregationRun:
        run = AggregationRun(run_type=run_type, status="running")
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        run._start_time = time.time()
        return run

    def _complete_run(self, run: AggregationRun, status: str, stats: dict[str, Any]) -> None:
        run.status = status
        run.providers_attempted = stats.get("providers_attempted", 0)
        run.providers_succeeded = stats.get("providers_succeeded", 0)
        run.providers_failed = stats.get("providers_failed", 0)
        run.jobs_created = stats.get("jobs_created", 0)
        run.jobs_updated = stats.get("jobs_updated", 0)
        run.jobs_expired = stats.get("jobs_expired", 0)
        run.walk_ins_created = stats.get("walk_ins_created", 0)
        run.walk_ins_updated = stats.get("walk_ins_updated", 0)
        run.duplicates_skipped = stats.get("duplicates_skipped", 0)
        run.errors = stats.get("errors", [])
        run.completed_at = datetime.utcnow()
        run.duration_seconds = round(time.time() - getattr(run, "_start_time", time.time()), 2)
        self.db.add(run)
        self.db.commit()

    def _serialize_run(self, run: AggregationRun) -> dict[str, Any]:
        return {
            "id": run.id,
            "run_type": run.run_type,
            "status": run.status,
            "providers_attempted": run.providers_attempted,
            "providers_succeeded": run.providers_succeeded,
            "providers_failed": run.providers_failed,
            "jobs_created": run.jobs_created,
            "jobs_updated": run.jobs_updated,
            "jobs_expired": run.jobs_expired,
            "walk_ins_created": run.walk_ins_created,
            "walk_ins_updated": run.walk_ins_updated,
            "duplicates_skipped": run.duplicates_skipped,
            "errors": run.errors or [],
            "duration_seconds": run.duration_seconds,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
        }
