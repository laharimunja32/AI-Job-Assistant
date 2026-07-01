from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job, JobSource, SearchHistory
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.base import JobProvider


class JobSearchService:
    """Coordinate provider searches, parsing, persistence, and filtering."""

    def __init__(self, db: Session, providers: list[JobProvider], parser: JobParserService | None = None, duplicate_detector: DuplicateDetectionService | None = None):
        self.db = db
        self.providers = providers
        self.parser = parser or JobParserService()
        self.duplicate_detector = duplicate_detector or DuplicateDetectionService()

    def search_jobs(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None, page: int = 1, size: int = 20) -> dict[str, Any]:
        filters = filters or {}
        items: list[dict[str, Any]] = []

        for provider in self.providers:
            raw_jobs = provider.search(keyword=keyword, location=location, filters=filters)
            for payload in raw_jobs:
                parsed = self.parser.parse_job_payload(payload)
                if self._matches_filters(parsed, filters):
                    self._upsert_job(parsed, provider.name)
                    items.append(self._serialize_job(parsed, provider.name))

        self._log_search(keyword=keyword, location=location, filters=filters, results_count=len(items))

        start = (page - 1) * size
        end = start + size
        return {"items": items[start:end], "total": len(items), "page": page, "size": size}

    def list_jobs(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(Job)
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(Job.title.ilike(search_term) | Job.description.ilike(search_term) | Job.company_name.ilike(search_term))
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if filters:
            if filters.get("work_mode"):
                query = query.filter(Job.work_mode.ilike(f"%{filters['work_mode']}%"))
            if filters.get("employment_type"):
                query = query.filter(Job.employment_type.ilike(f"%{filters['employment_type']}%"))
            if filters.get("experience_level"):
                query = query.filter(Job.experience.ilike(f"%{filters['experience_level']}%"))

        total = query.count()
        jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {"items": [self._job_to_payload(job) for job in jobs], "total": total, "page": page, "size": size}

    def save_job(self, payload: dict[str, Any]) -> Job:
        parsed = self.parser.parse_job_payload(payload)
        return self._upsert_job(parsed, parsed.get("source") or "unknown")

    def update_job(self, job_id: int, payload: dict[str, Any]) -> Job:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise ValueError("Job not found")
        for field in ["title", "company_name", "description", "skills", "experience", "education", "employment_type", "work_mode", "location", "salary", "apply_url", "source_name", "status", "tags", "external_id"]:
            if field in payload:
                setattr(job, field, payload[field])
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_expired_jobs(self, days: int = 30) -> int:
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)
        jobs = self.db.query(Job).filter(Job.updated_at < cutoff).all()
        for job in jobs:
            self.db.delete(job)
        self.db.commit()
        return len(jobs)

    def _upsert_job(self, parsed: dict[str, Any], provider_name: str) -> Job:
        existing = self.db.query(Job).filter(Job.apply_url == parsed.get("apply_url")).first()
        if existing is None:
            existing = self.db.query(Job).filter(Job.title == parsed.get("title"), Job.company_name == parsed.get("company"), Job.location == parsed.get("location")).first()

        if existing is None:
            source = self.db.query(JobSource).filter(JobSource.name == provider_name).first()
            if source is None:
                source = JobSource(name=provider_name, provider_name=provider_name, is_active=True)
                self.db.add(source)
                self.db.flush()

            job = Job(
                title=parsed.get("title") or "",
                company_name=parsed.get("company") or "Unknown",
                description=parsed.get("description"),
                skills=parsed.get("skills") or [],
                experience=parsed.get("experience"),
                education=parsed.get("education") or [],
                employment_type=parsed.get("employment_type"),
                work_mode=parsed.get("work_mode"),
                location=parsed.get("location"),
                salary=parsed.get("salary"),
                apply_url=parsed.get("apply_url"),
                source_name=provider_name,
                source_id=source.id,
                posted_date=parsed.get("posted_date"),
                last_updated=parsed.get("last_updated"),
                status=parsed.get("status") or "active",
                tags=parsed.get("tags") or [],
                external_id=parsed.get("external_id"),
            )
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            return job

        if parsed.get("description"):
            existing.description = parsed.get("description")
        if parsed.get("skills"):
            existing.skills = parsed.get("skills")
        if parsed.get("employment_type"):
            existing.employment_type = parsed.get("employment_type")
        if parsed.get("work_mode"):
            existing.work_mode = parsed.get("work_mode")
        if parsed.get("salary"):
            existing.salary = parsed.get("salary")
        if parsed.get("last_updated"):
            existing.last_updated = parsed.get("last_updated")
        if parsed.get("status"):
            existing.status = parsed.get("status")
        if parsed.get("tags"):
            existing.tags = parsed.get("tags")
        self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def _matches_filters(self, parsed: dict[str, Any], filters: dict[str, Any]) -> bool:
        if not filters:
            return True
        work_mode = filters.get("work_mode")
        if work_mode and parsed.get("work_mode") and work_mode.lower() not in str(parsed.get("work_mode")).lower():
            return False
        location = filters.get("location")
        if location and parsed.get("location") and location.lower() not in str(parsed.get("location")).lower():
            return False
        return True

    def _serialize_job(self, parsed: dict[str, Any], provider_name: str) -> dict[str, Any]:
        return {
            "title": parsed.get("title"),
            "company": parsed.get("company"),
            "location": parsed.get("location"),
            "description": parsed.get("description"),
            "skills": parsed.get("skills"),
            "experience": parsed.get("experience"),
            "employment_type": parsed.get("employment_type"),
            "work_mode": parsed.get("work_mode"),
            "salary": parsed.get("salary"),
            "apply_url": parsed.get("apply_url"),
            "source": provider_name,
            "posted_date": parsed.get("posted_date"),
            "tags": parsed.get("tags"),
        }

    def _job_to_payload(self, job: Job) -> dict[str, Any]:
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "description": job.description,
            "skills": job.skills,
            "experience": job.experience,
            "employment_type": job.employment_type,
            "work_mode": job.work_mode,
            "salary": job.salary,
            "apply_url": job.apply_url,
            "source": job.source_name,
            "posted_date": job.posted_date,
            "tags": job.tags,
        }

    def _log_search(self, keyword: str | None, location: str | None, filters: dict[str, Any] | None, results_count: int) -> None:
        history = SearchHistory(keyword=keyword, location=location, filters=filters or {}, results_count=results_count)
        self.db.add(history)
        self.db.commit()
