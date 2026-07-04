from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.job_search import LiveJobSearch
from app.schemas.job_search import JobSearchRequest
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.base import JobProvider
from app.services.jobs.search_service import JobSearchService


def _company_logo_url(company: str | None) -> str | None:
    if not company:
        return None
    initials = "".join(part[0].upper() for part in company.split()[:2] if part)
    return f"https://ui-avatars.com/api/?name={initials}&background=4f46e5&color=fff&size=128"


def _description_preview(description: str | None, max_len: int = 200) -> str | None:
    if not description:
        return None
    text = description.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _resolve_work_mode(request: JobSearchRequest) -> str | None:
    if request.remote:
        return "Remote"
    if request.hybrid:
        return "Hybrid"
    if request.onsite:
        return "On-site"
    return None


def _matches_date_posted(posted_date: datetime | None, date_posted: str | None) -> bool:
    if not date_posted or not posted_date:
        return True
    now = datetime.utcnow()
    posted = posted_date.replace(tzinfo=None) if posted_date.tzinfo else posted_date
    if date_posted.lower() == "today":
        return posted.date() == now.date()
    if date_posted.lower() == "week":
        return posted >= now - timedelta(days=7)
    if date_posted.lower() == "month":
        return posted >= now - timedelta(days=30)
    return True


class LiveJobSearchService:
    """Live job search with advanced filters, pagination, and search history."""

    def __init__(
        self,
        db: Session,
        providers: list[JobProvider] | None = None,
        parser: JobParserService | None = None,
        duplicate_detector: DuplicateDetectionService | None = None,
    ):
        from app.services.jobs.providers.sample_provider import SampleJobProvider

        self.db = db
        self.providers = providers or [SampleJobProvider()]
        self._base_service = JobSearchService(
            db=db,
            providers=self.providers,
            parser=parser or JobParserService(),
            duplicate_detector=duplicate_detector or DuplicateDetectionService(),
        )

    def search(self, user_id: int, request: JobSearchRequest) -> dict[str, Any]:
        work_mode = _resolve_work_mode(request)
        filters: dict[str, Any] = {
            "work_mode": work_mode,
            "employment_type": request.employment_type,
            "experience_level": request.experience,
            "company": request.company,
            "salary": request.salary,
            "date_posted": request.date_posted,
        }
        if request.remote:
            filters["remote"] = True
        if request.hybrid:
            filters["hybrid"] = True
        if request.onsite:
            filters["onsite"] = True

        raw = self._base_service.search_jobs(
            keyword=request.keyword,
            location=request.location,
            filters=filters,
            page=1,
            size=500,
        )

        items = []
        for item in raw["items"]:
            if request.company and item.get("company"):
                if request.company.lower() not in str(item["company"]).lower():
                    continue
            if request.salary and item.get("salary"):
                if request.salary.lower() not in str(item["salary"]).lower():
                    continue
            if request.experience and item.get("experience"):
                if request.experience.lower() not in str(item["experience"]).lower():
                    continue
            posted = item.get("posted_date")
            if isinstance(posted, str):
                try:
                    posted = datetime.fromisoformat(posted.replace("Z", "+00:00"))
                except ValueError:
                    posted = None
            if not _matches_date_posted(posted, request.date_posted):
                continue

            job_record = self._find_job_record(item)
            enriched = self._enrich_result(item, job_record)
            items.append(enriched)

        total = len(items)
        start = (request.page - 1) * request.size
        page_items = items[start : start + request.size]

        history = LiveJobSearch(
            user_id=user_id,
            keyword=request.keyword,
            location=request.location,
            company=request.company,
            salary=request.salary,
            experience=request.experience,
            employment_type=request.employment_type,
            work_mode=work_mode,
            date_posted=request.date_posted,
            filters=filters,
            results_count=total,
            page=request.page,
            size=request.size,
        )
        self.db.add(history)
        self.db.commit()

        return {"items": page_items, "total": total, "page": request.page, "size": request.size}

    def get_history(self, user_id: int, limit: int = 20) -> dict[str, Any]:
        query = (
            self.db.query(LiveJobSearch)
            .filter(LiveJobSearch.user_id == user_id)
            .order_by(LiveJobSearch.created_at.desc())
        )
        total = query.count()
        items = query.limit(limit).all()
        return {"items": items, "total": total}

    def get_search_by_id(self, user_id: int, search_id: int) -> LiveJobSearch | None:
        return (
            self.db.query(LiveJobSearch)
            .filter(LiveJobSearch.id == search_id, LiveJobSearch.user_id == user_id)
            .first()
        )

    def _find_job_record(self, item: dict[str, Any]) -> Job | None:
        apply_url = item.get("apply_url")
        if apply_url:
            job = self.db.query(Job).filter(Job.apply_url == apply_url).first()
            if job:
                return job
        title = item.get("title")
        company = item.get("company")
        if title and company:
            return (
                self.db.query(Job)
                .filter(Job.title == title, Job.company_name == company)
                .order_by(Job.created_at.desc())
                .first()
            )
        return None

    def _enrich_result(self, item: dict[str, Any], job: Job | None) -> dict[str, Any]:
        company = item.get("company") or (job.company_name if job else "Unknown")
        description = item.get("description") or (job.description if job else None)
        posted = item.get("posted_date") or (job.posted_date if job else None)
        if isinstance(posted, str):
            try:
                posted = datetime.fromisoformat(posted.replace("Z", "+00:00"))
            except ValueError:
                posted = None

        return {
            "id": job.id if job else None,
            "title": item.get("title") or (job.title if job else ""),
            "company": company,
            "salary": item.get("salary") or (job.salary if job else None),
            "location": item.get("location") or (job.location if job else None),
            "skills": item.get("skills") or (job.skills if job else []) or [],
            "employment_type": item.get("employment_type") or (job.employment_type if job else None),
            "experience": item.get("experience") or (job.experience if job else None),
            "posted_date": posted,
            "job_url": item.get("apply_url") or (job.apply_url if job else None),
            "company_logo": _company_logo_url(company),
            "description_preview": _description_preview(description),
            "work_mode": item.get("work_mode") or (job.work_mode if job else None),
        }
