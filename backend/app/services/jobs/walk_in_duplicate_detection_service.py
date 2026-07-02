from __future__ import annotations

from typing import Any

from app.db.models.walk_in import WalkInEvent


class WalkInDuplicateDetectionService:
    """Detect duplicate walk-in events using stable identifiers."""

    def is_duplicate(self, existing_event: WalkInEvent, payload: dict[str, Any]) -> bool:
        if existing_event.registration_url and payload.get("registration_url") and existing_event.registration_url == payload.get("registration_url"):
            return True

        normalized_existing = self._normalize(existing_event)
        normalized_payload = self._normalize(payload)
        return normalized_existing == normalized_payload

    def _normalize(self, value: Any) -> tuple[str, str, str, str]:
        if isinstance(value, WalkInEvent):
            return (
                (value.company_name or "").strip().lower(),
                (value.job_role or "").strip().lower(),
                (value.city or "").strip().lower(),
                str(value.walk_in_date or ""),
            )
        return (
            (value.get("company_name") or value.get("company") or "").strip().lower(),
            (value.get("job_role") or value.get("title") or "").strip().lower(),
            (value.get("city") or value.get("venue") or "").strip().lower(),
            str(value.get("walk_in_date") or ""),
        )
