from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.application import Application, ApplicationHistory
from app.db.models.browser_session import BrowserSession
from app.db.models.submission_review import SubmissionReviewAudit
from app.db.models.user import User
from app.schemas.browser import BrowserReviewConfirmRequest, BrowserReviewConfirmResponse, BrowserReviewReport, SubmissionValidationReport

logger = logging.getLogger(__name__)


class SubmissionAuditService:
    def record(
        self,
        *,
        db: Session,
        user: User,
        application: Application,
        browser_session: BrowserSession,
        review_report: BrowserReviewReport,
        validation_report: SubmissionValidationReport,
        payload: BrowserReviewConfirmRequest,
    ) -> BrowserReviewConfirmResponse:
        now = datetime.utcnow()
        result = "review_confirmed"
        next_status = application.status
        if payload.attempt_submission:
            result = "submitted" if validation_report.valid else "submission_failed"
            next_status = "submitted" if validation_report.valid else "submission_failed"
        elif review_report.readiness.score >= 85 and validation_report.valid:
            next_status = "ready_to_submit"
            result = "ready_to_submit"
        else:
            next_status = "review_required"
            result = "review_required"

        audit = SubmissionReviewAudit(
            user_id=user.id,
            application_id=application.id,
            session_id=browser_session.session_id,
            review_time_seconds=max(0, payload.review_time_seconds),
            readiness_score=review_report.readiness.score,
            validation_passed=validation_report.valid,
            validation_results=validation_report.model_dump(mode="json"),
            user_confirmation=payload.confirmed,
            submission_attempted=payload.attempt_submission,
            result=result,
            browser_session_status=browser_session.status,
            current_url=browser_session.current_url,
            warnings=review_report.page_warnings,
            errors=review_report.validation_errors,
            metadata_json={"confirmed_at": now.isoformat()},
        )
        db.add(audit)

        previous_status = application.status
        application.status = next_status
        if next_status == "submitted":
            application.applied_date = application.applied_date or now
        db.add(application)
        db.add(
            ApplicationHistory(
                application_id=application.id,
                user_id=user.id,
                from_status=previous_status,
                to_status=application.status,
                message="Guided review confirmation recorded",
                event_payload={
                    "review_result": result,
                    "readiness_score": review_report.readiness.score,
                    "validation_passed": validation_report.valid,
                    "submission_attempted": payload.attempt_submission,
                },
            )
        )
        db.commit()
        db.refresh(audit)
        db.refresh(application)

        logger.info(
            "submission_review_confirmed app=%s user=%s session=%s result=%s validation=%s",
            application.id,
            user.id,
            browser_session.session_id,
            result,
            validation_report.valid,
        )
        return BrowserReviewConfirmResponse(
            application_id=application.id,
            session_id=browser_session.session_id,
            result=result,
            status=application.status,
            confirmed=payload.confirmed,
            submission_attempted=payload.attempt_submission,
            timestamp=audit.created_at,
        )
