from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.application import Application, ApplicationHistory
from app.db.models.cover_letter import GeneratedCoverLetter
from app.db.models.job import Job
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import TailoredResume
from app.db.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User, payload: ApplicationCreate) -> Application:
        job = self.db.query(Job).filter(Job.id == payload.job_id).first()
        if job is None:
            raise ValueError("Job not found")
        self._validate_document_links(user.id, payload.selected_resume_id, payload.selected_tailored_resume_id, payload.selected_cover_letter_id)

        app = Application(
            user_id=user.id,
            job_id=payload.job_id,
            company_name=payload.company_name,
            job_title=payload.job_title,
            apply_url=payload.apply_url,
            selected_resume_id=payload.selected_resume_id,
            selected_tailored_resume_id=payload.selected_tailored_resume_id,
            selected_cover_letter_id=payload.selected_cover_letter_id,
            status=payload.status,
            source=payload.source,
            applied_date=payload.applied_date,
            notes=payload.notes,
            tags=payload.tags,
            priority=payload.priority,
            is_favorite=payload.is_favorite,
            follow_up_date=payload.follow_up_date,
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        self._create_history(app, None, app.status, "Application created")
        return app

    def update(self, user: User, application_id: int, payload: ApplicationUpdate) -> Application:
        app = self.get(user, application_id)
        if app is None:
            raise ValueError("Application not found")

        self._validate_document_links(
            user.id,
            payload.selected_resume_id if payload.selected_resume_id is not None else app.selected_resume_id,
            payload.selected_tailored_resume_id if payload.selected_tailored_resume_id is not None else app.selected_tailored_resume_id,
            payload.selected_cover_letter_id if payload.selected_cover_letter_id is not None else app.selected_cover_letter_id,
        )

        previous_status = app.status
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(app, key, value)

        if app.status == "applied" and app.applied_date is None:
            app.applied_date = datetime.utcnow()

        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)

        if previous_status != app.status:
            self._create_history(app, previous_status, app.status, "Application status updated")
        return app

    def delete(self, user: User, application_id: int, soft_delete: bool = True) -> None:
        app = self.get(user, application_id)
        if app is None:
            raise ValueError("Application not found")
        if soft_delete:
            app.is_deleted = True
            self.db.add(app)
            self.db.commit()
        else:
            self.db.delete(app)
            self.db.commit()

    def get(self, user: User, application_id: int) -> Application | None:
        return (
            self.db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user.id, Application.is_deleted.is_(False))
            .first()
        )

    def list(
        self,
        user: User,
        page: int = 1,
        size: int = 20,
        status: str | None = None,
        company: str | None = None,
        job_title: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
        favorites_only: bool = False,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        query = self.db.query(Application).filter(Application.user_id == user.id, Application.is_deleted.is_(False))
        if status:
            query = query.filter(Application.status == status)
        if company:
            query = query.filter(Application.company_name.ilike(f"%{company}%"))
        if job_title:
            query = query.filter(Application.job_title.ilike(f"%{job_title}%"))
        if start_date:
            query = query.filter(Application.created_at >= datetime.combine(start_date, time.min))
        if end_date:
            query = query.filter(Application.created_at <= datetime.combine(end_date, time.max))
        if search:
            query = query.filter((Application.company_name.ilike(f"%{search}%")) | (Application.job_title.ilike(f"%{search}%")))
        if favorites_only:
            query = query.filter(Application.is_favorite.is_(True))

        sort_column = getattr(Application, sort_by, Application.updated_at)
        sort_clause = sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc()
        query = query.order_by(sort_clause)

        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def history(self, user: User, application_id: int, page: int = 1, size: int = 20) -> dict[str, Any]:
        app = self.get(user, application_id)
        if app is None:
            raise ValueError("Application not found")
        query = self.db.query(ApplicationHistory).filter(
            ApplicationHistory.application_id == application_id,
            ApplicationHistory.user_id == user.id,
        )
        total = query.count()
        items = query.order_by(ApplicationHistory.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def _create_history(self, app: Application, from_status: str | None, to_status: str, message: str) -> None:
        history = ApplicationHistory(
            application_id=app.id,
            user_id=app.user_id,
            from_status=from_status,
            to_status=to_status,
            message=message,
            event_payload={"priority": app.priority, "is_favorite": app.is_favorite},
        )
        self.db.add(history)
        self.db.commit()

    def _validate_document_links(
        self,
        user_id: int,
        resume_id: int | None,
        tailored_resume_id: int | None,
        cover_letter_id: int | None,
    ) -> None:
        if resume_id is not None:
            resume = self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
            if resume is None:
                raise ValueError("Selected resume not found")
        if tailored_resume_id is not None:
            tailored = (
                self.db.query(TailoredResume)
                .filter(TailoredResume.id == tailored_resume_id, TailoredResume.user_id == user_id)
                .first()
            )
            if tailored is None:
                raise ValueError("Selected tailored resume not found")
        if cover_letter_id is not None:
            cover_letter = (
                self.db.query(GeneratedCoverLetter)
                .filter(GeneratedCoverLetter.id == cover_letter_id, GeneratedCoverLetter.user_id == user_id)
                .first()
            )
            if cover_letter is None:
                raise ValueError("Selected cover letter not found")
