from __future__ import annotations

from dataclasses import dataclass

from app.schemas.browser import (
    BrowserReviewReport,
    BrowserReviewSectionItem,
    BrowserSessionReadiness,
    FormFillResponse,
    SubmissionValidationReport,
    UploadStatusResponse,
)


@dataclass
class ReviewInputs:
    form_report: FormFillResponse | None
    upload_report: UploadStatusResponse | None
    validation_report: SubmissionValidationReport | None
    browser_status: str
    current_url: str | None


class ReviewService:
    def analyze(self, session_id: str, application_id: int, review_inputs: ReviewInputs) -> BrowserReviewReport:
        form = review_inputs.form_report
        upload = review_inputs.upload_report
        validation = review_inputs.validation_report

        filled_fields = [
            BrowserReviewSectionItem(
                key=item.field_id,
                label=item.field_type,
                value=item.value_preview or "filled",
                detail=item.reason,
            )
            for item in (form.filled_fields if form else [])
        ]
        empty_required_fields = [
            BrowserReviewSectionItem(
                key=item.field_id,
                label=item.field_type,
                value="missing",
                detail=item.reason,
            )
            for item in (form.required_manual_input if form else [])
        ]
        optional_fields = [
            BrowserReviewSectionItem(
                key=item.field_id,
                label=item.field_type,
                value=item.status,
                detail=item.reason,
            )
            for item in (form.unknown_fields if form else [])
        ]
        uploaded_documents = [
            BrowserReviewSectionItem(
                key=f"{item.field_type}:{item.selector}",
                label=item.document_type or item.field_type,
                value=item.filename or item.status,
                detail=item.status,
            )
            for item in (upload.uploaded_fields if upload else [])
        ]

        warnings = list(validation.warnings if validation else [])
        errors = list(validation.errors if validation else [])
        if review_inputs.browser_status != "active":
            warnings.append(f"Browser session status is '{review_inputs.browser_status}'")

        readiness_score = self._readiness(
            filled_count=len(filled_fields),
            required_missing_count=len(empty_required_fields),
            uploaded_count=len(uploaded_documents),
            validation_passed=bool(validation and validation.valid),
            warning_count=len(warnings),
            error_count=len(errors),
        )

        readiness = BrowserSessionReadiness(
            score=readiness_score,
            label=self._label(readiness_score),
            recommended_action="Proceed to submission confirmation" if readiness_score >= 85 else "Fix missing fields and retry validation",
        )
        return BrowserReviewReport(
            session_id=session_id,
            application_id=application_id,
            current_url=review_inputs.current_url,
            filled_fields=filled_fields,
            empty_required_fields=empty_required_fields,
            uploaded_documents=uploaded_documents,
            validation_errors=errors,
            optional_fields=optional_fields,
            page_warnings=warnings,
            readiness=readiness,
        )

    @staticmethod
    def _readiness(
        filled_count: int,
        required_missing_count: int,
        uploaded_count: int,
        validation_passed: bool,
        warning_count: int,
        error_count: int,
    ) -> int:
        score = 40
        score += min(filled_count * 4, 30)
        score += min(uploaded_count * 8, 20)
        if validation_passed:
            score += 15
        score -= required_missing_count * 12
        score -= warning_count * 4
        score -= error_count * 10
        return max(0, min(100, score))

    @staticmethod
    def _label(score: int) -> str:
        if score >= 85:
            return "ready"
        if score >= 60:
            return "needs_review"
        return "not_ready"
