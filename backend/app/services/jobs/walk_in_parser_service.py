from __future__ import annotations

from datetime import date, datetime
from typing import Any


class WalkInParserService:
    """Normalize raw provider payloads into the internal walk-in schema."""

    def parse_walk_in_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        skills = payload.get("skills") or []
        if isinstance(skills, str):
            skills = [skill.strip() for skill in skills.split(",") if skill.strip()]

        documents = payload.get("documents_required") or []
        if isinstance(documents, str):
            documents = [item.strip() for item in documents.split(",") if item.strip()]

        def _parse_date(value: Any) -> date | None:
            if isinstance(value, date) and not isinstance(value, datetime):
                return value
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value).date()
                except ValueError:
                    return None
            return None

        return {
            "company_name": payload.get("company_name") or payload.get("company") or "Unknown",
            "job_role": payload.get("job_role") or payload.get("title") or "Unknown",
            "job_description": payload.get("job_description") or payload.get("description") or "",
            "venue": payload.get("venue") or payload.get("location") or "",
            "city": payload.get("city") or payload.get("location") or "",
            "state": payload.get("state") or "",
            "walk_in_date": _parse_date(payload.get("walk_in_date") or payload.get("date")),
            "walk_in_time": payload.get("walk_in_time") or payload.get("time") or "",
            "registration_deadline": _parse_date(payload.get("registration_deadline") or payload.get("deadline")),
            "eligibility": payload.get("eligibility") or "",
            "degree": payload.get("degree") or "",
            "branch": payload.get("branch") or "",
            "passout_year": payload.get("passout_year") or payload.get("passout") or "",
            "skills": skills,
            "experience_required": payload.get("experience_required") or payload.get("experience") or "",
            "documents_required": documents,
            "contact_details": payload.get("contact_details") or payload.get("contact") or "",
            "registration_url": payload.get("registration_url") or payload.get("apply_url") or payload.get("url") or "",
            "source": payload.get("source") or "walk_in",
            "event_status": payload.get("event_status") or "Upcoming",
        }
