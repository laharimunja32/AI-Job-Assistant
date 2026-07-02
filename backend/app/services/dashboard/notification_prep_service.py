from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.user import User
from app.db.models.walk_in import WalkInEvent
from app.services.jobs.match_service import JobMatch


class NotificationPrepService:
    """Identifies notification candidates without sending notifications."""

    def __init__(self, db: Session):
        self.db = db

    def identify_candidates(self, user: User, since: datetime | None = None) -> dict[str, Any]:
        """Return categorized opportunities suitable for future notification modules."""
        since = since or datetime.utcnow() - timedelta(hours=24)
        return {
            "newly_matched_jobs": self._newly_matched_jobs(user, since),
            "newly_added_walk_ins": self._newly_added_walk_ins(since),
            "jobs_closing_soon": self._jobs_closing_soon(user),
            "high_priority_opportunities": self._high_priority_opportunities(user),
        }

    def _newly_matched_jobs(self, user: User, since: datetime) -> list[dict[str, Any]]:
        matches = (
            self.db.query(JobMatch)
            .filter(JobMatch.user_id == user.id, JobMatch.created_at >= since, JobMatch.score >= 70)
            .order_by(JobMatch.score.desc())
            .limit(20)
            .all()
        )
        job_ids = [m.job_id for m in matches]
        jobs = {j.id: j for j in self.db.query(Job).filter(Job.id.in_(job_ids)).all()} if job_ids else {}
        return [
            {
                "job_id": m.job_id,
                "title": jobs[m.job_id].title if m.job_id in jobs else None,
                "company": jobs[m.job_id].company_name if m.job_id in jobs else None,
                "score": m.score,
                "category": m.category,
                "matched_at": m.created_at,
            }
            for m in matches
            if m.job_id in jobs
        ]

    def _newly_added_walk_ins(self, since: datetime) -> list[dict[str, Any]]:
        events = (
            self.db.query(WalkInEvent)
            .filter(WalkInEvent.created_at >= since, WalkInEvent.event_status.in_(["Upcoming", "Today"]))
            .order_by(WalkInEvent.walk_in_date.asc())
            .limit(20)
            .all()
        )
        return [
            {
                "walk_in_id": e.id,
                "company_name": e.company_name,
                "job_role": e.job_role,
                "city": e.city,
                "walk_in_date": e.walk_in_date,
                "event_status": e.event_status,
            }
            for e in events
        ]

    def _jobs_closing_soon(self, user: User) -> list[dict[str, Any]]:
        today = date.today()
        deadline = today + timedelta(days=3)
        walk_ins = (
            self.db.query(WalkInEvent)
            .filter(
                WalkInEvent.walk_in_date <= deadline,
                WalkInEvent.walk_in_date >= today,
                WalkInEvent.event_status.in_(["Upcoming", "Today"]),
            )
            .order_by(WalkInEvent.walk_in_date.asc())
            .limit(10)
            .all()
        )
        return [
            {
                "type": "walk_in",
                "id": e.id,
                "title": e.job_role,
                "company": e.company_name,
                "deadline": e.registration_deadline or e.walk_in_date,
                "city": e.city,
            }
            for e in walk_ins
        ]

    def _high_priority_opportunities(self, user: User) -> list[dict[str, Any]]:
        matches = (
            self.db.query(JobMatch)
            .filter(JobMatch.user_id == user.id, JobMatch.score >= 90)
            .order_by(JobMatch.score.desc())
            .limit(10)
            .all()
        )
        job_ids = [m.job_id for m in matches]
        jobs = {j.id: j for j in self.db.query(Job).filter(Job.id.in_(job_ids), Job.status == "active").all()} if job_ids else {}
        return [
            {
                "job_id": m.job_id,
                "title": jobs[m.job_id].title,
                "company": jobs[m.job_id].company_name,
                "score": m.score,
                "category": m.category,
                "apply_url": jobs[m.job_id].apply_url,
                "work_mode": jobs[m.job_id].work_mode,
            }
            for m in matches
            if m.job_id in jobs
        ]
