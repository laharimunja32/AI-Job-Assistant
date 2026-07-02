from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

ASSESSMENT_STATUSES = {"Pending", "Scheduled", "Completed", "Expired", "Cancelled"}
INTERVIEW_STATUSES = {"Scheduled", "Completed", "Cancelled", "Rescheduled"}
TIMELINE_TYPES = {
    "Application Created",
    "Assessment",
    "Interview",
    "Offer",
    "Rejection",
    "Notes",
    "Status Changes",
    "Reminders",
}


class EmailProcessRequest(BaseModel):
    provider: str = Field(min_length=2, max_length=50)
    authorization_confirmed: bool = False
    sender: str = Field(min_length=3, max_length=255)
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(default="", max_length=10000)
    received_time: datetime


class EmailEventRead(BaseModel):
    id: int
    user_id: int
    application_id: int | None = None
    provider: str | None = None
    company_name: str | None = None
    job_title: str | None = None
    sender: str
    subject: str
    body_preview: str | None = None
    received_time: datetime
    event_type: str
    interview_invitation: bool
    online_assessment: bool
    coding_test: bool
    hr_round: bool
    technical_round: bool
    offer: bool
    rejection: bool
    deadline: datetime | None = None
    meeting_link: str | None = None
    is_read: bool
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailListResponse(BaseModel):
    items: list[EmailEventRead]
    total: int
    page: int
    size: int


class AssessmentBase(BaseModel):
    application_id: int | None = None
    email_event_id: int | None = None
    provider: str | None = Field(default=None, max_length=255)
    assessment_url: str | None = Field(default=None, max_length=1000)
    assessment_type: str | None = Field(default=None, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    deadline: datetime | None = None
    status: str = "Pending"
    notes: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().title()
        if normalized not in ASSESSMENT_STATUSES:
            raise ValueError("Invalid assessment status")
        return normalized


class AssessmentCreate(AssessmentBase):
    pass


class AssessmentUpdate(BaseModel):
    provider: str | None = Field(default=None, max_length=255)
    assessment_url: str | None = Field(default=None, max_length=1000)
    assessment_type: str | None = Field(default=None, max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    deadline: datetime | None = None
    status: str | None = None
    notes: str | None = None

    @field_validator("status")
    @classmethod
    def validate_optional_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().title()
        if normalized not in ASSESSMENT_STATUSES:
            raise ValueError("Invalid assessment status")
        return normalized


class AssessmentRead(AssessmentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentListResponse(BaseModel):
    items: list[AssessmentRead]
    total: int
    page: int
    size: int


class InterviewBase(BaseModel):
    application_id: int | None = None
    email_event_id: int | None = None
    interview_type: str = Field(min_length=2, max_length=100)
    interview_date: datetime | None = None
    interview_time: str | None = Field(default=None, max_length=50)
    time_zone: str | None = Field(default=None, max_length=100)
    meeting_link: str | None = Field(default=None, max_length=500)
    interviewer: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: str = "Scheduled"

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().title()
        if normalized not in INTERVIEW_STATUSES:
            raise ValueError("Invalid interview status")
        return normalized


class InterviewCreate(InterviewBase):
    pass


class InterviewUpdate(BaseModel):
    interview_type: str | None = Field(default=None, min_length=2, max_length=100)
    interview_date: datetime | None = None
    interview_time: str | None = Field(default=None, max_length=50)
    time_zone: str | None = Field(default=None, max_length=100)
    meeting_link: str | None = Field(default=None, max_length=500)
    interviewer: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def validate_optional_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().title()
        if normalized not in INTERVIEW_STATUSES:
            raise ValueError("Invalid interview status")
        return normalized


class InterviewRead(InterviewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewListResponse(BaseModel):
    items: list[InterviewRead]
    total: int
    page: int
    size: int


class TimelineEventRead(BaseModel):
    id: int
    user_id: int
    application_id: int
    event_type: str
    title: str
    description: str | None = None
    source_type: str | None = None
    source_id: int | None = None
    event_time: datetime
    metadata_json: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineResponse(BaseModel):
    items: list[TimelineEventRead]
    total: int


class ReminderCreate(BaseModel):
    application_id: int | None = None
    timeline_event_id: int | None = None
    title: str = Field(min_length=1, max_length=255)
    note: str | None = None
    due_at: datetime


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    note: str | None = None
    due_at: datetime | None = None
    status: str | None = None
    is_completed: bool | None = None


class ReminderRead(BaseModel):
    id: int
    user_id: int
    application_id: int | None = None
    timeline_event_id: int | None = None
    title: str
    note: str | None = None
    due_at: datetime
    status: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReminderListResponse(BaseModel):
    items: list[ReminderRead]
    total: int
    page: int
    size: int


class NotificationHistoryRead(BaseModel):
    id: int
    user_id: int
    application_id: int | None = None
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryListResponse(BaseModel):
    items: list[NotificationHistoryRead]
    total: int
    page: int
    size: int
