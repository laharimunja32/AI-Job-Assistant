from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.application import Application
from app.db.models.browser_session import BrowserSession, BrowserUploadAttempt
from app.db.models.cover_letter import GeneratedCoverLetter
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import TailoredResume
from app.db.models.user import User
from app.schemas.browser import UploadFieldDetection, UploadFieldStatus, UploadStatusResponse
from app.services.browser.upload_validation_service import UploadValidationService

logger = logging.getLogger(__name__)


class DocumentUploadService:
    def __init__(self, validation_service: UploadValidationService | None = None) -> None:
        self.validation = validation_service or UploadValidationService()

    def upload_documents(
        self,
        db: Session,
        page,  # noqa: ANN001
        session: BrowserSession,
        user: User,
        application: Application,
        detected_fields: list[UploadFieldDetection],
        include_resume: bool,
        include_cover_letter: bool,
        use_tailored_resume: bool,
    ) -> UploadStatusResponse:
        pending: list[UploadFieldStatus] = []
        uploaded: list[UploadFieldStatus] = []
        failed: list[UploadFieldStatus] = []

        resume_doc = self._resolve_resume_document(db, user, application, use_tailored_resume) if include_resume else None
        cover_doc = self._resolve_cover_document(db, user, application) if include_cover_letter else None

        for field in detected_fields:
            if field.field_type == "portfolio":
                pending.append(self._status(field, "detected_only", error="Portfolio detected; auto-upload disabled by policy"))
                continue
            if field.field_type in {"supporting_documents"}:
                pending.append(self._status(field, "skipped", error="Supporting documents require user confirmation"))
                continue

            document_path = None
            doc_type = None
            version = None
            if field.field_type == "resume" and resume_doc:
                document_path, doc_type, version = resume_doc
            if field.field_type == "cover_letter" and cover_doc:
                document_path, doc_type, version = cover_doc
            if not document_path:
                pending.append(self._status(field, "pending", error=f"No mapped document for {field.field_type}"))
                continue

            started = datetime.utcnow()
            started_perf = time.perf_counter()
            attempt = BrowserUploadAttempt(
                session_id=session.session_id,
                user_id=user.id,
                application_id=application.id,
                document_type=doc_type,
                document_version=version,
                filename=Path(document_path).name,
                selector=field.selector,
                started_at=started,
                confidence=field.confidence,
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)

            validation = self.validation.validate(page, field.selector, document_path)
            if not validation.accepted:
                attempt.success = False
                attempt.completed_at = datetime.utcnow()
                attempt.duration_ms = int((time.perf_counter() - started_perf) * 1000)
                attempt.error_message = validation.validation_error
                attempt.validation_messages = validation.messages
                db.add(attempt)
                db.commit()
                failed.append(self._status(field, "failed", doc_type, Path(document_path).name, validation, validation.validation_error, started, attempt.completed_at, attempt.duration_ms))
                continue

            try:
                self._perform_upload(page, field, document_path)
                ok, messages = self.validation.verify_upload(page, field.selector, Path(document_path).name)
                finished = datetime.utcnow()
                duration = int((time.perf_counter() - started_perf) * 1000)
                attempt.completed_at = finished
                attempt.duration_ms = duration
                attempt.success = ok
                attempt.validation_messages = messages
                if not ok:
                    attempt.error_message = "Filename confirmation failed"
                    failed.append(self._status(field, "failed", doc_type, Path(document_path).name, validation, attempt.error_message, started, finished, duration))
                else:
                    uploaded.append(self._status(field, "uploaded", doc_type, Path(document_path).name, validation, None, started, finished, duration))
                db.add(attempt)
                db.commit()
            except Exception as exc:  # pragma: no cover
                finished = datetime.utcnow()
                duration = int((time.perf_counter() - started_perf) * 1000)
                attempt.completed_at = finished
                attempt.duration_ms = duration
                attempt.success = False
                attempt.error_message = str(exc)
                db.add(attempt)
                db.commit()
                failed.append(self._status(field, "failed", doc_type, Path(document_path).name, validation, str(exc), started, finished, duration))

        status = "completed" if not failed else ("partial_success" if uploaded else "failed")
        return UploadStatusResponse(
            session_id=session.session_id,
            application_id=application.id,
            status=status,
            uploaded_fields=uploaded,
            failed_fields=failed,
            pending_fields=pending,
        )

    def build_status(self, db: Session, session: BrowserSession, application_id: int) -> UploadStatusResponse:
        rows = (
            db.query(BrowserUploadAttempt)
            .filter(
                BrowserUploadAttempt.session_id == session.session_id,
                BrowserUploadAttempt.user_id == session.user_id,
                BrowserUploadAttempt.application_id == application_id,
            )
            .order_by(BrowserUploadAttempt.started_at.desc())
            .all()
        )
        uploaded: list[UploadFieldStatus] = []
        failed: list[UploadFieldStatus] = []
        for row in rows:
            item = UploadFieldStatus(
                field_type=row.document_type,
                selector=row.selector or "",
                status="uploaded" if row.success else "failed",
                document_type=row.document_type,
                filename=row.filename,
                validation=None,
                error=row.error_message,
                started_at=row.started_at,
                completed_at=row.completed_at,
                duration_ms=row.duration_ms,
            )
            if row.success:
                uploaded.append(item)
            else:
                failed.append(item)
        status = "completed" if rows and not failed else ("partial_success" if uploaded else "pending")
        return UploadStatusResponse(
            session_id=session.session_id,
            application_id=application_id,
            status=status,
            uploaded_fields=uploaded,
            failed_fields=failed,
            pending_fields=[],
        )

    def _resolve_resume_document(self, db: Session, user: User, application: Application, use_tailored: bool) -> tuple[str, str, str] | None:
        if use_tailored and application.selected_tailored_resume_id:
            tailored = (
                db.query(TailoredResume)
                .filter(
                    TailoredResume.id == application.selected_tailored_resume_id,
                    TailoredResume.user_id == user.id,
                    TailoredResume.status == "completed",
                )
                .first()
            )
            if tailored and tailored.pdf_path and Path(tailored.pdf_path).exists():
                return tailored.pdf_path, "tailored_resume", f"v{tailored.resume_version}"
        if application.selected_resume_id:
            resume = db.query(Resume).filter(Resume.id == application.selected_resume_id, Resume.user_id == user.id).first()
        else:
            resume = (
                db.query(Resume)
                .filter(Resume.user_id == user.id, Resume.is_active.is_(True))
                .order_by(Resume.version.desc())
                .first()
            )
        if resume and Path(resume.storage_path).exists():
            return resume.storage_path, "resume", f"v{resume.version}"
        return None

    def _resolve_cover_document(self, db: Session, user: User, application: Application) -> tuple[str, str, str] | None:
        if not application.selected_cover_letter_id:
            return None
        cover = (
            db.query(GeneratedCoverLetter)
            .filter(
                GeneratedCoverLetter.id == application.selected_cover_letter_id,
                GeneratedCoverLetter.user_id == user.id,
                GeneratedCoverLetter.status == "completed",
            )
            .first()
        )
        if cover and cover.pdf_path and Path(cover.pdf_path).exists():
            return cover.pdf_path, "cover_letter", f"v{cover.cover_letter_version}"
        return None

    def _perform_upload(self, page, field: UploadFieldDetection, file_path: str) -> None:  # noqa: ANN001
        locator = page.locator(field.selector).first
        if field.upload_capability in {"standard", "hidden_input"} or (field.input_type or "").lower() == "file":
            locator.set_input_files(file_path)
            page.wait_for_timeout(500)
            return
        locator.click()
        page.wait_for_timeout(300)
        try:
            page.set_input_files("input[type='file']", file_path, timeout=2000)
        except Exception:
            page.locator("input[type='file']").first.set_input_files(file_path)
        page.wait_for_timeout(500)

    @staticmethod
    def _status(
        field: UploadFieldDetection,
        status: str,
        document_type: str | None = None,
        filename: str | None = None,
        validation=None,  # noqa: ANN001
        error: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_ms: int | None = None,
    ) -> UploadFieldStatus:
        return UploadFieldStatus(
            field_type=field.field_type,
            selector=field.selector,
            status=status,
            document_type=document_type,
            filename=filename,
            confidence=field.confidence,
            visible=field.visible,
            upload_capability=field.upload_capability,
            validation=validation,
            error=error,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
        )
