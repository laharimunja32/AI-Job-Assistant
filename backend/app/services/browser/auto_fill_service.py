from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.schemas.browser import DetectedFormField, FormFillFieldResult, FormFillResponse


@dataclass
class UserFormData:
    values: dict[str, str]


class AutoFillService:
    def build_user_data(self, db: Session, user: User) -> UserFormData:
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        active_resume = (
            db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active.is_(True)).order_by(Resume.version.desc()).first()
        )

        full_name = (user.full_name or "").strip()
        first_name, last_name = self._split_name(full_name)
        location = (profile.location if profile else None) or ""
        city, state, country = self._split_location(location)
        highest_education = (profile.education[0] if profile and profile.education else {}) if profile else {}
        work_preferences = profile.work_preferences if profile and isinstance(profile.work_preferences, dict) else {}
        resume_metadata = active_resume.file_metadata if active_resume and isinstance(active_resume.file_metadata, dict) else {}

        values = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": user.email,
            "phone_number": (profile.phone if profile else "") or "",
            "address": (profile.address if profile else "") or "",
            "city": city,
            "state": state,
            "country": country,
            "postal_code": str(resume_metadata.get("postal_code", "")),
            "date_of_birth": str(resume_metadata.get("date_of_birth", "")),
            "linkedin_url": (profile.linkedin_url if profile else "") or "",
            "github_url": (profile.github_url if profile else "") or "",
            "portfolio_url": (profile.portfolio_url if profile else "") or "",
            "highest_qualification": str(
                highest_education.get("degree")
                or highest_education.get("qualification")
                or resume_metadata.get("highest_qualification", "")
            ),
            "university": str(highest_education.get("institution") or resume_metadata.get("university", "")),
            "graduation_year": str(resume_metadata.get("graduation_year", "")),
            "current_company": str(resume_metadata.get("current_company", "")),
            "current_role": str(resume_metadata.get("current_role", "")),
            "experience": str(resume_metadata.get("experience_years", "")),
            "skills": ", ".join((profile.skills if profile and profile.skills else [])[:20]),
            "notice_period": str(work_preferences.get("availability", "")),
            "current_salary": str(resume_metadata.get("current_salary", "")),
            "expected_salary": str(resume_metadata.get("expected_salary", "")),
            "work_authorization": str(resume_metadata.get("work_authorization", "")),
            "willing_to_relocate": self._bool_to_text(work_preferences.get("relocation")),
            "resume_upload": "",
            "cover_letter_upload": "",
        }
        return UserFormData(values=values)

    def fill_fields(
        self,
        page,  # noqa: ANN001
        session_id: str,
        detected_fields: list[DetectedFormField],
        user_data: UserFormData,
        overrides: dict[str, str] | None = None,
        traverse_steps: bool = True,
    ) -> FormFillResponse:
        overrides = overrides or {}
        filled: list[FormFillFieldResult] = []
        skipped: list[FormFillFieldResult] = []
        unknown: list[FormFillFieldResult] = []
        required_manual: list[FormFillFieldResult] = []

        for field in detected_fields:
            if field.input_type == "password":
                skipped.append(self._result(field, "skipped", "Password fields are intentionally not auto-filled"))
                continue
            if field.field_type in {"resume_upload", "cover_letter_upload"}:
                skipped.append(self._result(field, "skipped", "File upload automation is out of scope"))
                if field.required:
                    required_manual.append(self._result(field, "manual_required", "Manual file upload required"))
                continue

            value = overrides.get(field.field_id) or user_data.values.get(field.field_type, "")
            if not value:
                unknown.append(self._result(field, "unknown", "No mapping value available"))
                if field.required:
                    required_manual.append(self._result(field, "manual_required", "Required field needs manual input"))
                continue

            try:
                locator = page.locator(field.selector).first
                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "select":
                    locator.select_option(label=value)
                elif field.input_type == "checkbox":
                    should_check = value.lower() in {"yes", "true", "1"}
                    if should_check:
                        locator.check()
                    else:
                        locator.uncheck()
                else:
                    locator.fill(value)
                filled.append(self._result(field, "filled", value_preview=self._mask_value(field.field_type, value)))
            except Exception as exc:  # pragma: no cover - dependent on external pages
                skipped.append(self._result(field, "skipped", f"Fill failed: {exc}"))
                if field.required:
                    required_manual.append(self._result(field, "manual_required", "Required field fill failed"))

        if traverse_steps:
            self._try_advance_step(page)

        mapped_total = len(filled) + len(unknown) + len(skipped)
        completion = round((len(filled) / mapped_total) * 100, 1) if mapped_total else 0.0
        return FormFillResponse(
            session_id=session_id,
            page_url=page.url if hasattr(page, "url") else None,
            completion_percentage=completion,
            filled_fields=filled,
            skipped_fields=skipped,
            unknown_fields=unknown,
            required_manual_input=required_manual,
        )

    @staticmethod
    def _split_name(full_name: str) -> tuple[str, str]:
        if not full_name:
            return "", ""
        parts = [part for part in full_name.split(" ") if part]
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])

    @staticmethod
    def _split_location(location: str) -> tuple[str, str, str]:
        chunks = [chunk.strip() for chunk in location.split(",") if chunk.strip()]
        if len(chunks) == 0:
            return "", "", ""
        if len(chunks) == 1:
            return chunks[0], "", ""
        if len(chunks) == 2:
            return chunks[0], chunks[1], ""
        return chunks[0], chunks[1], chunks[2]

    @staticmethod
    def _bool_to_text(value: object) -> str:
        if value is True:
            return "Yes"
        if value is False:
            return "No"
        return ""

    @staticmethod
    def _try_advance_step(page) -> None:  # noqa: ANN001
        try:
            for label in ("Next", "Continue", "Proceed"):
                button = page.get_by_role("button", name=label)
                if button.count() > 0:
                    button.first.click()
                    break
        except Exception:
            return

    @staticmethod
    def _mask_value(field_type: str, value: str) -> str:
        if field_type == "email" and "@" in value:
            name, _, domain = value.partition("@")
            return f"{name[:2]}***@{domain}"
        if field_type == "phone_number" and len(value) >= 4:
            return f"***{value[-4:]}"
        return value[:80]

    @staticmethod
    def _result(field: DetectedFormField, status: str, reason: str | None = None, value_preview: str | None = None) -> FormFillFieldResult:
        return FormFillFieldResult(
            field_id=field.field_id,
            field_type=field.field_type,
            selector=field.selector,
            status=status,
            reason=reason,
            value_preview=value_preview,
        )
