from __future__ import annotations

from app.schemas.browser import FormDetectionResponse, SubmissionValidationReport, UploadStatusResponse


class SubmissionValidationService:
    def validate(
        self,
        *,
        session_active: bool,
        has_resume_selection: bool,
        has_cover_letter_selection: bool,
        cover_letter_required: bool,
        detection: FormDetectionResponse | None,
        upload_status: UploadStatusResponse | None,
    ) -> SubmissionValidationReport:
        checks: dict[str, bool] = {}
        warnings: list[str] = []
        errors: list[str] = []

        checks["browser_session_active"] = session_active
        if not session_active:
            errors.append("Browser session is not active")

        required_fields = [f for f in (detection.fields if detection else []) if f.required]
        missing_required = [f.field_type for f in required_fields if not (f.value or "").strip()]
        checks["required_fields_completed"] = len(missing_required) == 0
        if missing_required:
            errors.append("Required fields missing: " + ", ".join(missing_required[:8]))

        resume_uploaded = self._has_uploaded(upload_status, {"resume", "tailored_resume"})
        checks["resume_uploaded"] = resume_uploaded or has_resume_selection
        if not checks["resume_uploaded"]:
            errors.append("Resume must be uploaded before submission")

        checks["cover_letter_required"] = cover_letter_required
        cover_uploaded = self._has_uploaded(upload_status, {"cover_letter"})
        checks["cover_letter_uploaded_if_required"] = (not cover_letter_required) or cover_uploaded or has_cover_letter_selection
        if cover_letter_required and not checks["cover_letter_uploaded_if_required"]:
            errors.append("Cover letter is required for this application")

        checks["file_upload_success"] = not bool(upload_status and upload_status.failed_fields)
        if upload_status and upload_status.failed_fields:
            errors.append("One or more file uploads failed")

        mandatory_checkboxes = [
            f
            for f in required_fields
            if (f.input_type or "").lower() == "checkbox" or "terms" in (f.field_type or "").lower()
        ]
        checks["mandatory_checkboxes_acknowledged"] = len(mandatory_checkboxes) == 0
        if mandatory_checkboxes:
            warnings.append("Mandatory checkbox acknowledgements may need manual verification")

        valid = all(checks.values()) and not errors
        return SubmissionValidationReport(valid=valid, checks=checks, warnings=warnings, errors=errors)

    @staticmethod
    def _has_uploaded(upload_status: UploadStatusResponse | None, doc_types: set[str]) -> bool:
        if upload_status is None:
            return False
        return any((field.document_type or field.field_type) in doc_types for field in upload_status.uploaded_fields)
