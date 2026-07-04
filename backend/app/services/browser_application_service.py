from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.application import Application
from app.db.models.application_history import BrowserAutomationRecord
from app.db.models.job import Job
from app.schemas.browser_application import BrowserApplicationStartRequest, BrowserApplicationSubmitRequest
from app.schemas.browser import FormDetectionResponse
from app.db.models.user import User
from app.services.browser.auto_fill_service import AutoFillService
from app.services.browser.document_upload_service import DocumentUploadService
from app.services.browser.form_detection_service import FormDetectionService
from app.services.browser.navigation_service import NavigationService
from app.services.browser.review_service import ReviewInputs, ReviewService
from app.services.browser.submission_validation_service import SubmissionValidationService
from app.services.browser.upload_detection_service import UploadDetectionService


class BrowserApplicationService:
    """Orchestrates end-to-end browser-assisted job applications."""

    def __init__(self, db: Session, browser_manager: Any | None = None):
        self.db = db
        self.browser_manager = browser_manager

    def start_application(self, user: User, payload: BrowserApplicationStartRequest) -> BrowserAutomationRecord:
        started = time.monotonic()
        apply_url = payload.apply_url
        job = None
        if payload.job_id:
            job = self.db.query(Job).filter(Job.id == payload.job_id).first()
            if job and not apply_url:
                apply_url = job.apply_url

        job_id = payload.job_id or (job.id if job else self._ensure_placeholder_job(payload))

        application = Application(
            user_id=user.id,
            job_id=job_id,
            company_name=payload.company_name,
            job_title=payload.job_title,
            apply_url=apply_url,
            selected_resume_id=payload.resume_id,
            selected_cover_letter_id=payload.cover_letter_id,
            status="in_progress",
            source="browser_automation",
        )
        self.db.add(application)
        self.db.flush()

        record = BrowserAutomationRecord(
            user_id=user.id,
            application_id=application.id,
            job_id=job_id,
            company_name=payload.company_name,
            job_title=payload.job_title,
            status="started",
            resume_id=payload.resume_id,
            cover_letter_id=payload.cover_letter_id,
            metadata_json={"steps": ["started"]},
        )

        error_message: str | None = None
        final_status = "started"
        form_report = None
        upload_report = None

        if self.browser_manager is not None and apply_url:
            try:
                browser_type = payload.browser_type or settings.playwright_browser
                session = self.browser_manager.create_session(
                    self.db,
                    user_id=user.id,
                    browser_type=browser_type,
                    application_id=application.id,
                )
                record.browser_session_id = session.session_id
                record.metadata_json["steps"].append("session_created")

                nav = NavigationService(self.browser_manager)
                metadata = nav.open_apply_url(session, apply_url)
                session.current_url = metadata.final_url
                record.metadata_json["steps"].append("navigated")

                page = self.browser_manager.get_page(session.session_id)
                if page is not None:
                    form_service = FormDetectionService()
                    fields = form_service.detect_fields(page)
                    detection = FormDetectionResponse(
                        session_id=session.session_id,
                        page_url=page.url if hasattr(page, "url") else session.current_url,
                        fields=fields,
                        total_fields=len(fields),
                    )
                    self.browser_manager.cache_form_detection(session.session_id, detection)
                    record.metadata_json["forms_detected"] = len(fields)

                    auto_fill = AutoFillService()
                    user_data = auto_fill.build_user_data(self.db, user)
                    form_report = auto_fill.fill_fields(
                        page=page,
                        session_id=session.session_id,
                        detected_fields=fields,
                        user_data=user_data,
                    )
                    self.browser_manager.cache_form_report(session.session_id, form_report)
                    record.metadata_json["fields_filled"] = len(form_report.filled_fields)
                    record.metadata_json["steps"].append("autofilled")

                    upload_service = UploadDetectionService()
                    upload_fields = upload_service.detect_fields(page)
                    if upload_fields:
                        doc_upload = DocumentUploadService()
                        upload_report = doc_upload.upload_documents(
                            db=self.db,
                            page=page,
                            session=session,
                            user=user,
                            application=application,
                            detected_fields=upload_fields,
                            include_resume=payload.resume_id is not None,
                            include_cover_letter=payload.cover_letter_id is not None,
                            use_tailored_resume=False,
                        )
                        record.metadata_json["uploads"] = upload_report.model_dump()
                        record.metadata_json["steps"].append("uploaded")

                    validation = SubmissionValidationService().validate(
                        session_active=session.status == "active",
                        has_resume_selection=application.selected_resume_id is not None,
                        has_cover_letter_selection=application.selected_cover_letter_id is not None,
                        cover_letter_required=bool(
                            any("cover" in (field.field_type or "").lower() and field.required for field in fields)
                        ),
                        detection=detection,
                        upload_status=upload_report,
                    )
                    review = ReviewService().analyze(
                        session.session_id,
                        application.id,
                        ReviewInputs(
                            form_report=form_report,
                            upload_report=upload_report,
                            validation_report=validation,
                            browser_status=session.status,
                            current_url=session.current_url,
                        ),
                    )
                    record.metadata_json["readiness_score"] = review.readiness.score
                    record.metadata_json["steps"].append("reviewed")

                    if review.empty_required_fields or review.validation_errors:
                        final_status = "manual_required"
            except Exception as exc:
                error_message = str(exc)
                final_status = "failed"
                record.metadata_json["steps"].append("failed")
        elif not apply_url:
            final_status = "manual_required"
            error_message = "No apply URL provided; manual application required"
        else:
            final_status = "manual_required"
            error_message = "Browser manager unavailable; configure Playwright to enable automation"

        duration = time.monotonic() - started
        record.status = final_status
        record.duration_seconds = round(duration, 2)
        record.error_message = error_message
        application.status = "review_required" if final_status == "manual_required" else application.status

        self.db.add(record)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(record)
        return record

    def submit_application(
        self,
        user: User,
        record_id: int,
        payload: BrowserApplicationSubmitRequest,
    ) -> BrowserAutomationRecord:
        record = self._get_record(user.id, record_id)
        if record.status == "completed":
            return record

        started = time.monotonic()
        if not payload.confirm:
            record.status = "manual_required"
            record.error_message = "Submission not confirmed by user"
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

        record.status = "completed"
        record.applied_date = datetime.utcnow()
        steps = record.metadata_json.get("steps", []) if record.metadata_json else []
        steps.append("submitted")
        record.metadata_json = {**(record.metadata_json or {}), "steps": steps}
        record.duration_seconds = (record.duration_seconds or 0) + round(time.monotonic() - started, 2)

        if record.application_id:
            application = self.db.query(Application).filter(Application.id == record.application_id).first()
            if application:
                application.status = "submitted"
                application.applied_date = record.applied_date
                self.db.add(application)

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_history(self, user_id: int, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = (
            self.db.query(BrowserAutomationRecord)
            .filter(BrowserAutomationRecord.user_id == user_id)
            .order_by(BrowserAutomationRecord.created_at.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def get_by_id(self, user_id: int, record_id: int) -> BrowserAutomationRecord | None:
        return self._get_record(user_id, record_id, raise_not_found=False)

    def automation_success_rate(self, user_id: int) -> float:
        records = self.db.query(BrowserAutomationRecord).filter(BrowserAutomationRecord.user_id == user_id).all()
        if not records:
            return 100.0
        completed = sum(1 for r in records if r.status == "completed")
        return round((completed / len(records)) * 100, 1)

    def applications_today(self, user_id: int) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return (
            self.db.query(BrowserAutomationRecord)
            .filter(
                BrowserAutomationRecord.user_id == user_id,
                BrowserAutomationRecord.status == "completed",
                BrowserAutomationRecord.applied_date >= today_start,
            )
            .count()
        )

    def applications_this_week(self, user_id: int) -> int:
        week_start = datetime.utcnow() - __import__("datetime").timedelta(days=7)
        return (
            self.db.query(BrowserAutomationRecord)
            .filter(
                BrowserAutomationRecord.user_id == user_id,
                BrowserAutomationRecord.status == "completed",
                BrowserAutomationRecord.applied_date >= week_start,
            )
            .count()
        )

    def recent_applications(self, user_id: int, limit: int = 5) -> list[BrowserAutomationRecord]:
        return (
            self.db.query(BrowserAutomationRecord)
            .filter(BrowserAutomationRecord.user_id == user_id)
            .order_by(BrowserAutomationRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def _get_record(
        self,
        user_id: int,
        record_id: int,
        raise_not_found: bool = True,
    ) -> BrowserAutomationRecord | None:
        record = (
            self.db.query(BrowserAutomationRecord)
            .filter(BrowserAutomationRecord.id == record_id, BrowserAutomationRecord.user_id == user_id)
            .first()
        )
        if record is None and raise_not_found:
            raise ValueError("Browser application record not found")
        return record

    def _ensure_placeholder_job(self, payload: BrowserApplicationStartRequest) -> int:
        job = Job(
            title=payload.job_title,
            company_name=payload.company_name,
            apply_url=payload.apply_url,
            source_name="browser_automation",
            status="active",
        )
        self.db.add(job)
        self.db.flush()
        return job.id
