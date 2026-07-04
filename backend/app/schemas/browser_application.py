from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrowserApplicationStartRequest(BaseModel):
    job_id: int | None = None
    job_title: str
    company_name: str
    apply_url: str | None = None
    resume_id: int | None = None
    cover_letter_id: int | None = None
    browser_type: str | None = None


class BrowserApplicationSubmitRequest(BaseModel):
    confirm: bool = True
    notes: str | None = None


class BrowserApplicationRead(BaseModel):
    id: int
    application_id: int | None = None
    job_id: int | None = None
    company_name: str
    job_title: str
    status: str
    browser_session_id: str | None = None
    resume_id: int | None = None
    cover_letter_id: int | None = None
    duration_seconds: float | None = None
    applied_date: datetime | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrowserApplicationListResponse(BaseModel):
    items: list[BrowserApplicationRead]
    total: int
    page: int
    size: int
