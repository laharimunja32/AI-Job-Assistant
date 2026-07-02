from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.aggregation import AggregationRun
from app.db.models.application import Application
from app.db.models.browser_session import BrowserSession
from app.db.models.submission_review import SubmissionReviewAudit
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.db.models.walk_in import WalkInEvent
from app.services.dashboard.cache import DashboardCache
from app.services.jobs.match_service import JobMatch, JobMatchService
from app.services.cover_letter_service import CoverLetterService
from app.services.recruitment_monitoring_service import RecruitmentMonitoringService
from app.services.resume_tailoring_service import ResumeTailoringService

logger = logging.getLogger(__name__)


class DashboardService:
    """Prepares personalized dashboard data using the logged-in user's profile and resume."""

    def __init__(self, db: Session, cache: DashboardCache | None = None, match_service: JobMatchService | None = None):
        self.db = db
        self.cache = cache or DashboardCache()
        self.match_service = match_service or JobMatchService(db=db)
        self.resume_tailoring = ResumeTailoringService(db=db)
        self.cover_letters = CoverLetterService(db=db)
        self.recruitment_monitoring = RecruitmentMonitoringService(db=db)

    def get_full_dashboard(self, user: User, page: int = 1, size: int = 10) -> dict[str, Any]:
        cached = self.cache.get("full_dashboard", user.id, suffix=f"{page}:{size}")
        if cached is not None:
            return cached

        self._ensure_matches(user)
        profile = self._get_profile(user)

        result = {
            "new_jobs": self.get_new_jobs(user, page=1, size=size),
            "new_jobs_today": self.get_new_jobs_today(user, page=1, size=size),
            "high_match_jobs": self.get_high_match_jobs(user, page=1, size=size),
            "recommended_jobs": self.get_recommended_jobs(user, page=1, size=size),
            "walk_ins": self.get_walk_ins(user, page=1, size=size),
            "todays_walk_ins": self.get_todays_walk_ins(user, page=1, size=size),
            "upcoming_walk_ins": self.get_upcoming_walk_ins(user, page=1, size=size),
            "remote_jobs": self.get_remote_jobs(user, page=1, size=size),
            "hybrid_jobs": self.get_hybrid_jobs(user, page=1, size=size),
            "jobs_by_city": self.get_jobs_by_city(user),
            "recent_companies": self.get_recent_companies(user, page=1, size=size),
            "closing_soon": self.get_closing_soon(user, page=1, size=size),
            "recently_updated_jobs": self.get_recently_updated_jobs(user, page=1, size=size),
            "statistics": self.get_statistics(user),
            "profile_summary": self._profile_summary(profile),
            "recent_tailored_resumes": self.resume_tailoring.recent_for_dashboard(user),
            "resume_generation_history": self.resume_tailoring.history_for_dashboard(user),
            "resume_ats_average": self.resume_tailoring.ats_average_for_dashboard(user),
            "resume_improvement_suggestions": self.resume_tailoring.suggestions_for_dashboard(user),
            "recent_cover_letters": self.cover_letters.recent_for_dashboard(user),
            "cover_letter_generation_history": self.cover_letters.history_for_dashboard(user),
            "recent_cover_letter_templates": self.cover_letters.template_usage_for_dashboard(user),
            "cover_letter_statistics": self.cover_letters.stats_for_dashboard(user),
            "recruitment_summary": self.recruitment_monitoring.dashboard_summary(user),
        }
        self.cache.set("full_dashboard", user.id, result, suffix=f"{page}:{size}")
        return result

    def get_new_jobs(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = self._base_job_query(user).filter(Job.created_at >= cutoff, Job.status == "active")
        return self._paginate_jobs_with_scores(query.order_by(Job.created_at.desc()), user, page, size)

    def get_new_jobs_today(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = self._base_job_query(user).filter(Job.created_at >= today_start, Job.status == "active")
        return self._paginate_jobs_with_scores(query.order_by(Job.created_at.desc()), user, page, size)

    def get_high_match_jobs(self, user: User, min_score: int = 90, page: int = 1, size: int = 20) -> dict[str, Any]:
        self._ensure_matches(user)
        matches = (
            self.db.query(JobMatch)
            .filter(JobMatch.user_id == user.id, JobMatch.score >= min_score)
            .order_by(JobMatch.score.desc())
        )
        total = matches.count()
        items = matches.offset((page - 1) * size).limit(size).all()
        job_ids = [m.job_id for m in items]
        jobs = {j.id: j for j in self.db.query(Job).filter(Job.id.in_(job_ids), Job.status == "active").all()} if job_ids else {}
        serialized = []
        for match in items:
            job = jobs.get(match.job_id)
            if job:
                serialized.append(self._serialize_job_with_match(job, match))
        return {"items": serialized, "total": total, "page": page, "size": size}

    def get_recommended_jobs(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        self._ensure_matches(user)
        profile = self._get_profile(user)
        query = self._base_job_query(user).filter(Job.status == "active")

        if profile and profile.preferred_job_roles:
            role_filters = [Job.title.ilike(f"%{role}%") for role in profile.preferred_job_roles if isinstance(role, str)]
            if role_filters:
                from sqlalchemy import or_

                query = query.filter(or_(*role_filters))

        matches = {m.job_id: m for m in self.db.query(JobMatch).filter(JobMatch.user_id == user.id).all()}
        all_jobs = query.all()
        scored_jobs = [(job, matches.get(job.id)) for job in all_jobs if matches.get(job.id)]
        scored_jobs.sort(key=lambda pair: pair[1].score if pair[1] else 0, reverse=True)

        total = len(scored_jobs)
        start = (page - 1) * size
        page_items = scored_jobs[start : start + size]
        return {
            "items": [self._serialize_job_with_match(job, match) for job, match in page_items if match],
            "total": total,
            "page": page,
            "size": size,
        }

    def get_walk_ins(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self._personalized_walk_in_query(user)
        return self._paginate_walk_ins(query.order_by(WalkInEvent.walk_in_date.asc()), page, size)

    def get_todays_walk_ins(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        today = date.today()
        query = self._personalized_walk_in_query(user).filter(WalkInEvent.walk_in_date == today)
        return self._paginate_walk_ins(query, page, size)

    def get_upcoming_walk_ins(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        today = date.today()
        query = self._personalized_walk_in_query(user).filter(WalkInEvent.walk_in_date >= today)
        return self._paginate_walk_ins(query.order_by(WalkInEvent.walk_in_date.asc()), page, size)

    def get_remote_jobs(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self._base_job_query(user).filter(Job.status == "active", Job.work_mode.ilike("%remote%"))
        return self._paginate_jobs_with_scores(query.order_by(Job.created_at.desc()), user, page, size)

    def get_hybrid_jobs(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self._base_job_query(user).filter(Job.status == "active", Job.work_mode.ilike("%hybrid%"))
        return self._paginate_jobs_with_scores(query.order_by(Job.created_at.desc()), user, page, size)

    def get_jobs_by_city(self, user: User) -> dict[str, Any]:
        query = (
            self._base_job_query(user)
            .filter(Job.status == "active", Job.location.isnot(None))
            .with_entities(Job.location, func.count(Job.id))
            .group_by(Job.location)
            .order_by(func.count(Job.id).desc())
            .limit(20)
        )
        cities = [{"city": loc, "count": count} for loc, count in query.all() if loc]
        return {"cities": cities, "total_cities": len(cities)}

    def get_recent_companies(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=30)
        subquery = (
            self.db.query(Job.company_name, func.max(Job.created_at).label("latest"))
            .filter(Job.status == "active", Job.created_at >= cutoff)
            .group_by(Job.company_name)
            .subquery()
        )
        query = self.db.query(subquery.c.company_name, subquery.c.latest).order_by(subquery.c.latest.desc())
        total = query.count()
        rows = query.offset((page - 1) * size).limit(size).all()
        return {
            "items": [{"company_name": name, "latest_job_at": latest} for name, latest in rows],
            "total": total,
            "page": page,
            "size": size,
        }

    def get_closing_soon(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        today = date.today()
        deadline_cutoff = today + timedelta(days=3)
        walk_in_query = self._personalized_walk_in_query(user).filter(
            WalkInEvent.walk_in_date <= deadline_cutoff,
            WalkInEvent.walk_in_date >= today,
            WalkInEvent.event_status.in_(["Upcoming", "Today"]),
        )
        walk_ins = walk_in_query.order_by(WalkInEvent.walk_in_date.asc()).all()

        stale_cutoff = datetime.utcnow() - timedelta(days=25)
        job_query = self._base_job_query(user).filter(
            Job.status == "active",
            Job.posted_date.isnot(None),
            Job.posted_date <= stale_cutoff,
        )
        jobs = job_query.order_by(Job.posted_date.asc()).limit(size).all()

        items: list[dict[str, Any]] = []
        for event in walk_ins:
            items.append({"type": "walk_in", **self._serialize_walk_in(event)})
        for job in jobs:
            match = self._get_match_for_job(user, job.id)
            items.append({"type": "job", **self._serialize_job_with_match(job, match)})

        total = len(items)
        start = (page - 1) * size
        return {"items": items[start : start + size], "total": total, "page": page, "size": size}

    def get_recently_updated_jobs(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self._base_job_query(user).filter(Job.status == "active")
        return self._paginate_jobs_with_scores(query.order_by(Job.updated_at.desc()), user, page, size)

    def get_statistics(self, user: User) -> dict[str, Any]:
        self._ensure_matches(user)
        profile = self._get_profile(user)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today = date.today()

        total_active_jobs = self.db.query(Job).filter(Job.status == "active").count()
        new_today = self.db.query(Job).filter(Job.status == "active", Job.created_at >= today_start).count()
        walk_ins_today = self.db.query(WalkInEvent).filter(WalkInEvent.walk_in_date == today).count()
        walk_ins_upcoming = self.db.query(WalkInEvent).filter(WalkInEvent.walk_in_date >= today).count()
        remote_count = self.db.query(Job).filter(Job.status == "active", Job.work_mode.ilike("%remote%")).count()
        hybrid_count = self.db.query(Job).filter(Job.status == "active", Job.work_mode.ilike("%hybrid%")).count()

        matches = self.db.query(JobMatch).filter(JobMatch.user_id == user.id).all()
        high_matches = sum(1 for m in matches if m.score >= 90)
        strong_matches = sum(1 for m in matches if m.score >= 80)
        avg_score = round(sum(m.score for m in matches) / len(matches), 1) if matches else 0.0

        last_run = self.db.query(AggregationRun).order_by(AggregationRun.started_at.desc()).first()
        app_query = self.db.query(Application).filter(Application.user_id == user.id, Application.is_deleted.is_(False))
        total_applications = app_query.count()
        draft_applications = app_query.filter(Application.status == "draft").count()
        ready_to_apply = app_query.filter(Application.status == "ready_to_apply").count()
        applied_today = app_query.filter(Application.applied_date >= today_start).count()
        interviews = app_query.filter(
            Application.status.in_(["interview_scheduled", "technical_interview", "hr_interview"])
        ).count()
        offers = app_query.filter(Application.status.in_(["offer_received", "offer_accepted"])).count()
        rejections = app_query.filter(Application.status == "rejected").count()
        favorites = app_query.filter(Application.is_favorite.is_(True)).count()
        browser_sessions = self.db.query(BrowserSession).filter(BrowserSession.user_id == user.id).all()
        browser_active = sum(1 for s in browser_sessions if s.status == "active")
        browser_closed = sum(1 for s in browser_sessions if s.status == "closed")
        browser_failed = sum(1 for s in browser_sessions if s.status == "failed")
        browser_success_denom = browser_closed + browser_failed
        browser_success_rate = (browser_closed / browser_success_denom) * 100 if browser_success_denom else 100.0
        browser_last_activity = max((s.last_activity for s in browser_sessions), default=None)
        browser_status = "healthy" if browser_failed == 0 else "degraded"
        ready_to_submit = app_query.filter(Application.status == "ready_to_submit").count()
        applications_under_review = app_query.filter(Application.status == "review_required").count()
        submitted_today = app_query.filter(Application.status == "submitted", Application.updated_at >= today_start).count()
        audits = self.db.query(SubmissionReviewAudit).filter(SubmissionReviewAudit.user_id == user.id).all()
        validation_failures = sum(1 for item in audits if not item.validation_passed)
        average_readiness_score = round(sum(item.readiness_score for item in audits) / len(audits), 1) if audits else 0.0
        recruitment_summary = self.recruitment_monitoring.dashboard_summary(user)

        return {
            "total_active_jobs": total_active_jobs,
            "new_jobs_today": new_today,
            "walk_ins_today": walk_ins_today,
            "walk_ins_upcoming": walk_ins_upcoming,
            "remote_jobs": remote_count,
            "hybrid_jobs": hybrid_count,
            "total_matches": len(matches),
            "high_matches": high_matches,
            "strong_matches": strong_matches,
            "average_match_score": avg_score,
            "profile_completeness": self._profile_completeness(profile),
            "last_aggregation_at": last_run.completed_at if last_run else None,
            "total_applications": total_applications,
            "draft_applications": draft_applications,
            "ready_to_apply": ready_to_apply,
            "applied_today": applied_today,
            "interviews": interviews,
            "offers": offers,
            "rejections": rejections,
            "favorites": favorites,
            "browser_active_sessions": browser_active,
            "browser_navigation_success_rate": round(browser_success_rate, 1),
            "browser_last_activity": browser_last_activity,
            "browser_status": browser_status,
            "ready_to_submit": ready_to_submit,
            "applications_under_review": applications_under_review,
            "submitted_today": submitted_today,
            "validation_failures": validation_failures,
            "average_readiness_score": average_readiness_score,
            "upcoming_assessments": recruitment_summary["upcoming_assessments"],
            "upcoming_interviews": recruitment_summary["upcoming_interviews"],
            "unread_recruitment_emails": recruitment_summary["unread_recruitment_emails"],
            "todays_deadlines": recruitment_summary["todays_deadlines"],
        }

    def refresh_user_feed(self, user: User) -> dict[str, Any]:
        """Recompute matches and invalidate cached dashboard data for the user."""
        self.cache.invalidate_user(user.id)
        matches = self.match_service.match_all_jobs(user)
        return {
            "matches_computed": len(matches),
            "high_matches": sum(1 for m in matches if m.score >= 90),
            "average_score": round(sum(m.score for m in matches) / len(matches), 1) if matches else 0.0,
        }

    def _ensure_matches(self, user: User) -> None:
        existing_count = self.db.query(JobMatch).filter(JobMatch.user_id == user.id).count()
        active_jobs = self.db.query(Job).filter(Job.status == "active").count()
        if existing_count < active_jobs:
            self.match_service.match_all_jobs(user)

    def _get_profile(self, user: User) -> Profile | None:
        return self.db.query(Profile).filter(Profile.user_id == user.id).first()

    def _get_active_resume(self, user: User) -> Resume | None:
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user.id, Resume.is_active.is_(True))
            .order_by(Resume.version.desc())
            .first()
        )

    def _base_job_query(self, user: User):
        """Filter jobs by user profile preferences when available."""
        query = self.db.query(Job).filter(Job.external_id.is_(None) | ~Job.external_id.like("walkin:%"))
        profile = self._get_profile(user)
        if profile is None:
            return query

        from sqlalchemy import or_

        if profile.preferred_locations:
            loc_filters = [Job.location.ilike(f"%{loc}%") for loc in profile.preferred_locations if isinstance(loc, str)]
            if loc_filters:
                query = query.filter(or_(*loc_filters) | Job.work_mode.ilike("%remote%"))

        return query

    def _personalized_walk_in_query(self, user: User):
        query = self.db.query(WalkInEvent).filter(WalkInEvent.event_status.in_(["Upcoming", "Today"]))
        profile = self._get_profile(user)
        if profile is None:
            return query

        from sqlalchemy import or_

        if profile.preferred_locations:
            loc_filters = [WalkInEvent.city.ilike(f"%{loc}%") for loc in profile.preferred_locations if isinstance(loc, str)]
            if loc_filters:
                query = query.filter(or_(*loc_filters))

        return query

    def _get_match_for_job(self, user: User, job_id: int) -> JobMatch | None:
        return self.db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job_id).first()

    def _paginate_jobs_with_scores(self, query, user: User, page: int, size: int) -> dict[str, Any]:
        total = query.count()
        jobs = query.offset((page - 1) * size).limit(size).all()
        items = []
        for job in jobs:
            match = self._get_match_for_job(user, job.id)
            items.append(self._serialize_job_with_match(job, match))
        return {"items": items, "total": total, "page": page, "size": size}

    def _paginate_walk_ins(self, query, page: int, size: int) -> dict[str, Any]:
        total = query.count()
        events = query.offset((page - 1) * size).limit(size).all()
        return {"items": [self._serialize_walk_in(e) for e in events], "total": total, "page": page, "size": size}

    def _serialize_job_with_match(self, job: Job, match: JobMatch | None) -> dict[str, Any]:
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
            "status": job.status,
            "tags": job.tags,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "match_score": match.score if match else None,
            "match_category": match.category if match else None,
            "matched_skills": match.matched_skills if match else [],
        }

    def _serialize_walk_in(self, event: WalkInEvent) -> dict[str, Any]:
        return {
            "id": event.id,
            "company_name": event.company_name,
            "job_role": event.job_role,
            "venue": event.venue,
            "city": event.city,
            "state": event.state,
            "walk_in_date": event.walk_in_date,
            "walk_in_time": event.walk_in_time,
            "registration_deadline": event.registration_deadline,
            "eligibility": event.eligibility,
            "skills": event.skills,
            "experience_required": event.experience_required,
            "registration_url": event.registration_url,
            "source": event.source,
            "event_status": event.event_status,
            "created_at": event.created_at,
        }

    def _profile_summary(self, profile: Profile | None) -> dict[str, Any]:
        if profile is None:
            return {"has_profile": False, "skills_count": 0, "preferred_roles": [], "preferred_locations": []}
        return {
            "has_profile": True,
            "skills_count": len(profile.skills or []),
            "preferred_roles": profile.preferred_job_roles or [],
            "preferred_locations": profile.preferred_locations or [],
            "education_count": len(profile.education or []),
            "certifications_count": len(profile.certifications or []),
            "profile_completeness": self._profile_completeness(profile),
        }

    def _profile_completeness(self, profile: Profile | None) -> float:
        if profile is None:
            return 0.0
        fields = [
            bool(profile.skills),
            bool(profile.education),
            bool(profile.preferred_job_roles),
            bool(profile.preferred_locations or profile.location),
            bool(profile.certifications),
            bool(profile.projects),
        ]
        return round(sum(fields) / len(fields) * 100, 1)
