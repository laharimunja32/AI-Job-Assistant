from __future__ import annotations

from datetime import datetime
from typing import Any


class JobParserService:
    """Normalize raw provider payloads into the internal job schema."""

    def parse_job_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = payload.get("title") or payload.get("job_title") or ""
        company = payload.get("company") or payload.get("company_name") or "Unknown"
        location = payload.get("location") or payload.get("city") or ""
        description = payload.get("description") or payload.get("summary") or ""
        skills = payload.get("skills") or []
        if isinstance(skills, str):
            skills = [skill.strip() for skill in skills.split(",") if skill.strip()]
        work_mode = (payload.get("work_mode") or "").strip() or "Unknown"
        employment_type = (payload.get("employment_type") or "").strip() or "Unknown"
        tags = payload.get("tags") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

        posted_date = payload.get("posted_date")
        if isinstance(posted_date, str):
            try:
                posted_date = datetime.fromisoformat(posted_date)
            except ValueError:
                posted_date = None

        return {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "skills": skills,
            "experience": payload.get("experience"),
            "education": payload.get("education") or [],
            "employment_type": employment_type,
            "work_mode": work_mode,
            "salary": payload.get("salary"),
            "apply_url": payload.get("apply_url") or payload.get("url"),
            "source": payload.get("source") or "unknown",
            "posted_date": posted_date,
            "last_updated": payload.get("last_updated") or posted_date,
            "status": payload.get("status") or "active",
            "tags": tags,
            "external_id": payload.get("external_id") or payload.get("id"),
        }
