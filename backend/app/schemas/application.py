from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

APPLICATION_STATUSES = {
    "draft",
    "ready_to_apply",
    "applied",
    "assessment_received",
    "interview_scheduled",
    "technical_interview",
    "hr_interview",
    "offer_received",
    "offer_accepted",
    "offer_declined",
    "rejected",
    "withdrawn",
    "ready_to_submit",
    "review_required",
    "submitted",
    "submission_failed",
}


class ApplicationCreate(BaseModel):
    job_id: int
    company_name: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    apply_url: str | None = Field(default=None, max_length=500)
    selected_resume_id: int | None = None
    selected_tailored_resume_id: int | None = None
    selected_cover_letter_id: int | None = None
    status: str = "draft"
    source: str | None = Field(default=None, max_length=100)
    applied_date: datetime | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=2, ge=1, le=5)
    is_favorite: bool = False
    follow_up_date: datetime | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in APPLICATION_STATUSES:
            raise ValueError("Invalid application status")
        return normalized


class ApplicationUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    job_title: str | None = Field(default=None, min_length=1, max_length=255)
    apply_url: str | None = Field(default=None, max_length=500)
    selected_resume_id: int | None = None
    selected_tailored_resume_id: int | None = None
    selected_cover_letter_id: int | None = None
    status: str | None = None
    source: str | None = Field(default=None, max_length=100)
    applied_date: datetime | None = None
    notes: str | None = None
    tags: list[str] | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    is_favorite: bool | None = None
    follow_up_date: datetime | None = None

    @field_validator("status")
    @classmethod
    def validate_optional_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in APPLICATION_STATUSES:
            raise ValueError("Invalid application status")
        return normalized


class ApplicationNotesUpdate(BaseModel):
    notes: str | None = None


class ApplicationPriorityUpdate(BaseModel):
    priority: int = Field(ge=1, le=5)


class ApplicationFavoriteUpdate(BaseModel):
    is_favorite: bool


class ApplicationRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    company_name: str
    job_title: str
    apply_url: str | None = None
    selected_resume_id: int | None = None
    selected_tailored_resume_id: int | None = None
    selected_cover_letter_id: int | None = None
    status: str
    source: str | None = None
    applied_date: datetime | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    priority: int
    is_favorite: bool
    follow_up_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    interview_prepared: bool = False
    interview_completed: bool = False
    interview_readiness_score: float | None = None
    interview_practice_sessions: int = 0
    interview_preparation_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationListResponse(BaseModel):
    items: list[ApplicationRead]
    total: int
    page: int
    size: int


class ApplicationHistoryRead(BaseModel):
    id: int
    application_id: int
    user_id: int
    from_status: str | None = None
    to_status: str
    message: str | None = None
    event_payload: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationHistoryResponse(BaseModel):
    items: list[ApplicationHistoryRead]
    total: int
    page: int
    size: int
