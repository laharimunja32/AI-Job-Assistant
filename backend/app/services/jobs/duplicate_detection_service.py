from __future__ import annotations

from typing import Any

from app.db.models.job import Job


class DuplicateDetectionService:
    """Detect duplicates based on a small set of stable fields."""

    def is_duplicate(self, existing_job: Job, payload: dict[str, Any]) -> bool:
        if existing_job.apply_url and payload.get("apply_url") and existing_job.apply_url == payload.get("apply_url"):
            return True

        normalized_existing = self._normalize(existing_job)
        normalized_payload = self._normalize(payload)
        return normalized_existing == normalized_payload

    def _normalize(self, value: Any) -> tuple[str, str, str]:
        if isinstance(value, Job):
            return (
                (value.title or "").strip().lower(),
                (value.company_name or "").strip().lower(),
                (value.location or "").strip().lower(),
            )
        return (
            (value.get("title") or "").strip().lower(),
            (value.get("company") or "").strip().lower(),
            (value.get("location") or "").strip().lower(),
        )
