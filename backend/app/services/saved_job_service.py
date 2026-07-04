from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.saved_job import SavedJob
from app.schemas.saved_job import SavedJobCreate


class SavedJobService:
    """Manage user-saved job postings."""

    def __init__(self, db: Session):
        self.db = db

    def save_job(self, user_id: int, payload: SavedJobCreate) -> SavedJob:
        if payload.job_id is not None:
            existing = (
                self.db.query(SavedJob)
                .filter(SavedJob.user_id == user_id, SavedJob.job_id == payload.job_id)
                .first()
            )
            if existing:
                return existing

        record = SavedJob(
            user_id=user_id,
            job_id=payload.job_id,
            job_title=payload.job_title,
            company_name=payload.company_name,
            salary=payload.salary,
            location=payload.location,
            skills=payload.skills,
            employment_type=payload.employment_type,
            experience=payload.experience,
            posted_date=payload.posted_date,
            job_url=payload.job_url,
            company_logo=payload.company_logo,
            description_preview=payload.description_preview,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def remove_job(self, user_id: int, saved_job_id: int) -> bool:
        record = (
            self.db.query(SavedJob)
            .filter(SavedJob.id == saved_job_id, SavedJob.user_id == user_id)
            .first()
        )
        if record is None:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def list_saved_jobs(self, user_id: int, page: int = 1, size: int = 20) -> dict:
        query = self.db.query(SavedJob).filter(SavedJob.user_id == user_id).order_by(SavedJob.saved_at.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def check_saved_status(self, user_id: int, job_id: int | None = None, saved_job_id: int | None = None) -> dict:
        query = self.db.query(SavedJob).filter(SavedJob.user_id == user_id)
        if job_id is not None:
            record = query.filter(SavedJob.job_id == job_id).first()
        elif saved_job_id is not None:
            record = query.filter(SavedJob.id == saved_job_id).first()
        else:
            return {"job_id": job_id, "saved_job_id": None, "is_saved": False}

        if record is None:
            return {"job_id": job_id, "saved_job_id": None, "is_saved": False}
        return {"job_id": record.job_id, "saved_job_id": record.id, "is_saved": True}

    def count_saved_jobs(self, user_id: int) -> int:
        return self.db.query(SavedJob).filter(SavedJob.user_id == user_id).count()

    def recent_saved_jobs(self, user_id: int, limit: int = 5) -> list[SavedJob]:
        return (
            self.db.query(SavedJob)
            .filter(SavedJob.user_id == user_id)
            .order_by(SavedJob.saved_at.desc())
            .limit(limit)
            .all()
        )
