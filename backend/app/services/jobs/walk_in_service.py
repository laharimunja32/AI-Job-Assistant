from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.walk_in import WalkInEvent
from app.services.jobs.walk_in_duplicate_detection_service import WalkInDuplicateDetectionService
from app.services.jobs.walk_in_parser_service import WalkInParserService
from app.services.jobs.providers.walkin_provider import WalkInProvider


class WalkInEventService:
    """Coordinate provider discovery, parsing, persistence, and filtering for walk-in drives."""

    def __init__(self, db: Session, providers: list[WalkInProvider], parser: WalkInParserService | None = None, duplicate_detector: WalkInDuplicateDetectionService | None = None):
        self.db = db
        self.providers = providers
        self.parser = parser or WalkInParserService()
        self.duplicate_detector = duplicate_detector or WalkInDuplicateDetectionService()

    def refresh_walk_ins(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        created = 0
        updated = 0
        for provider in self.providers:
            raw_events = provider.search(keyword=keyword, location=location, filters=filters)
            for payload in raw_events:
                parsed = self.parser.parse_walk_in_payload(payload)
                parsed["event_status"] = self._resolve_event_status(parsed.get("walk_in_date"), parsed.get("event_status"))
                event, is_new = self._upsert_event(parsed, provider.name)
                if is_new:
                    created += 1
                else:
                    updated += 1
                self._sync_to_job(event)

        self.cleanup_expired_events()
        return {"created": created, "updated": updated, "total": self.db.query(WalkInEvent).count()}

    def list_walk_ins(self, page: int = 1, size: int = 20) -> dict[str, Any]:
        return self.search_walk_ins(page=page, size=size)

    def get_todays_walk_ins(self, page: int = 1, size: int = 20) -> dict[str, Any]:
        today = date.today()
        query = self.db.query(WalkInEvent).filter(WalkInEvent.walk_in_date == today)
        return self._paginate(query, page, size)

    def get_upcoming_walk_ins(self, page: int = 1, size: int = 20) -> dict[str, Any]:
        today = date.today()
        query = self.db.query(WalkInEvent).filter(WalkInEvent.walk_in_date >= today)
        return self._paginate(query, page, size)

    def search_walk_ins(self, company: str | None = None, role: str | None = None, city: str | None = None, eligibility: str | None = None, walk_in_date: date | str | None = None, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(WalkInEvent)
        if company:
            query = query.filter(WalkInEvent.company_name.ilike(f"%{company}%"))
        if role:
            query = query.filter(WalkInEvent.job_role.ilike(f"%{role}%"))
        if city:
            query = query.filter(WalkInEvent.city.ilike(f"%{city}%"))
        if eligibility:
            query = query.filter(WalkInEvent.eligibility.ilike(f"%{eligibility}%"))
        if walk_in_date:
            if isinstance(walk_in_date, str):
                try:
                    walk_in_date = datetime.fromisoformat(walk_in_date).date()
                except ValueError:
                    walk_in_date = None
            if walk_in_date:
                query = query.filter(WalkInEvent.walk_in_date == walk_in_date)
        return self._paginate(query.order_by(WalkInEvent.walk_in_date.asc(), WalkInEvent.created_at.desc()), page, size)

    def cleanup_expired_events(self, days: int = 30) -> int:
        today = date.today()
        stale_events = self.db.query(WalkInEvent).filter(WalkInEvent.walk_in_date < today, WalkInEvent.event_status.in_(["Upcoming", "Today"])).all()
        for event in stale_events:
            event.event_status = "Completed"
        self.db.commit()

        cutoff = today - timedelta(days=days)
        old_completed = self.db.query(WalkInEvent).filter(WalkInEvent.event_status == "Completed", WalkInEvent.walk_in_date < cutoff).all()
        for event in old_completed:
            self.db.delete(event)
        self.db.commit()
        return len(stale_events)

    def _upsert_event(self, parsed: dict[str, Any], provider_name: str) -> tuple[WalkInEvent, bool]:
        existing = self._find_existing_event(parsed)

        if existing is None:
            event = WalkInEvent(
                company_name=parsed.get("company_name") or "Unknown",
                job_role=parsed.get("job_role") or "Unknown",
                job_description=parsed.get("job_description"),
                venue=parsed.get("venue"),
                city=parsed.get("city"),
                state=parsed.get("state"),
                walk_in_date=parsed.get("walk_in_date"),
                walk_in_time=parsed.get("walk_in_time"),
                registration_deadline=parsed.get("registration_deadline"),
                eligibility=parsed.get("eligibility"),
                degree=parsed.get("degree"),
                branch=parsed.get("branch"),
                passout_year=parsed.get("passout_year"),
                skills=parsed.get("skills") or [],
                experience_required=parsed.get("experience_required"),
                documents_required=parsed.get("documents_required") or [],
                contact_details=parsed.get("contact_details"),
                registration_url=parsed.get("registration_url"),
                source=parsed.get("source") or provider_name,
                event_status=parsed.get("event_status") or "Upcoming",
            )
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event, True

        if parsed.get("job_description"):
            existing.job_description = parsed.get("job_description")
        if parsed.get("venue"):
            existing.venue = parsed.get("venue")
        if parsed.get("city"):
            existing.city = parsed.get("city")
        if parsed.get("state"):
            existing.state = parsed.get("state")
        if parsed.get("walk_in_date"):
            existing.walk_in_date = parsed.get("walk_in_date")
        if parsed.get("walk_in_time"):
            existing.walk_in_time = parsed.get("walk_in_time")
        if parsed.get("registration_deadline"):
            existing.registration_deadline = parsed.get("registration_deadline")
        if parsed.get("eligibility"):
            existing.eligibility = parsed.get("eligibility")
        if parsed.get("degree"):
            existing.degree = parsed.get("degree")
        if parsed.get("branch"):
            existing.branch = parsed.get("branch")
        if parsed.get("passout_year"):
            existing.passout_year = parsed.get("passout_year")
        if parsed.get("skills"):
            existing.skills = parsed.get("skills")
        if parsed.get("experience_required"):
            existing.experience_required = parsed.get("experience_required")
        if parsed.get("documents_required"):
            existing.documents_required = parsed.get("documents_required")
        if parsed.get("contact_details"):
            existing.contact_details = parsed.get("contact_details")
        if parsed.get("registration_url"):
            existing.registration_url = parsed.get("registration_url")
        if parsed.get("source"):
            existing.source = parsed.get("source")
        if parsed.get("event_status"):
            existing.event_status = parsed.get("event_status")
        self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)
        return existing, False

    def _find_existing_event(self, parsed: dict[str, Any]) -> WalkInEvent | None:
        registration_url = parsed.get("registration_url")
        if registration_url:
            existing = self.db.query(WalkInEvent).filter(WalkInEvent.registration_url == registration_url).first()
            if existing is not None:
                return existing

        company_name = parsed.get("company_name")
        job_role = parsed.get("job_role")
        if company_name and job_role:
            candidates = (
                self.db.query(WalkInEvent)
                .filter(WalkInEvent.company_name == company_name, WalkInEvent.job_role == job_role)
                .all()
            )
            for candidate in candidates:
                if self.duplicate_detector.is_duplicate(candidate, parsed):
                    return candidate
        return None

    @staticmethod
    def _resolve_event_status(walk_in_date: date | None, event_status: str | None) -> str:
        if event_status == "Cancelled":
            return "Cancelled"
        if walk_in_date is None:
            return event_status or "Upcoming"
        today = date.today()
        if walk_in_date < today:
            return "Completed"
        if walk_in_date == today:
            return "Today"
        return "Upcoming"

    def _sync_to_job(self, event: WalkInEvent) -> Job:
        existing_job = self.db.query(Job).filter(Job.external_id == f"walkin:{event.id}").first()
        if existing_job is None:
            existing_job = self.db.query(Job).filter(Job.apply_url == event.registration_url).first()
        if existing_job is None:
            existing_job = Job(
                title=event.job_role,
                company_name=event.company_name,
                description=self._compose_job_description(event),
                skills=event.skills or [],
                experience=event.experience_required,
                education=[event.degree, event.branch] if event.degree or event.branch else [],
                employment_type="Walk-in",
                work_mode="Onsite",
                location=f"{event.city or ''}, {event.state or ''}".strip(", "),
                apply_url=event.registration_url,
                source_name="walk-in",
                posted_date=event.walk_in_date,
                last_updated=event.updated_at,
                status="active" if event.event_status != "Cancelled" else "cancelled",
                tags=[event.eligibility, event.event_status, "walk-in"] if event.eligibility or event.event_status else ["walk-in"],
                external_id=f"walkin:{event.id}",
            )
            self.db.add(existing_job)
            self.db.commit()
            self.db.refresh(existing_job)
            return existing_job

        existing_job.title = event.job_role
        existing_job.company_name = event.company_name
        existing_job.description = self._compose_job_description(event)
        existing_job.skills = event.skills or []
        existing_job.experience = event.experience_required
        existing_job.education = [event.degree, event.branch] if event.degree or event.branch else []
        existing_job.work_mode = "Onsite"
        existing_job.location = f"{event.city or ''}, {event.state or ''}".strip(", ")
        existing_job.apply_url = event.registration_url
        existing_job.posted_date = event.walk_in_date
        existing_job.last_updated = event.updated_at
        existing_job.status = "active" if event.event_status != "Cancelled" else "cancelled"
        existing_job.tags = [event.eligibility, event.event_status, "walk-in"] if event.eligibility or event.event_status else ["walk-in"]
        self.db.add(existing_job)
        self.db.commit()
        self.db.refresh(existing_job)
        return existing_job

    def _compose_job_description(self, event: WalkInEvent) -> str:
        pieces = [event.job_description or "Walk-in drive opportunity."]
        if event.venue:
            pieces.append(f"Venue: {event.venue}")
        if event.walk_in_date:
            pieces.append(f"Walk-in Date: {event.walk_in_date}")
        if event.walk_in_time:
            pieces.append(f"Walk-in Time: {event.walk_in_time}")
        if event.registration_deadline:
            pieces.append(f"Registration Deadline: {event.registration_deadline}")
        return " | ".join(pieces)

    def _paginate(self, query, page: int, size: int) -> dict[str, Any]:
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": [self._serialize_walk_in(item) for item in items], "total": total, "page": page, "size": size}

    def _serialize_walk_in(self, event: WalkInEvent) -> dict[str, Any]:
        return {
            "id": event.id,
            "company_name": event.company_name,
            "job_role": event.job_role,
            "job_description": event.job_description,
            "venue": event.venue,
            "city": event.city,
            "state": event.state,
            "walk_in_date": event.walk_in_date,
            "walk_in_time": event.walk_in_time,
            "registration_deadline": event.registration_deadline,
            "eligibility": event.eligibility,
            "degree": event.degree,
            "branch": event.branch,
            "passout_year": event.passout_year,
            "skills": event.skills,
            "experience_required": event.experience_required,
            "documents_required": event.documents_required,
            "contact_details": event.contact_details,
            "registration_url": event.registration_url,
            "source": event.source,
            "event_status": event.event_status,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }
