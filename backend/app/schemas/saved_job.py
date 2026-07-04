from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedJobCreate(BaseModel):
    job_id: int | None = None
    job_title: str
    company_name: str
    salary: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    experience: str | None = None
    posted_date: datetime | None = None
    job_url: str | None = None
    company_logo: str | None = None
    description_preview: str | None = None


class SavedJobRead(BaseModel):
    id: int
    job_id: int | None = None
    job_title: str
    company_name: str
    salary: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    experience: str | None = None
    posted_date: datetime | None = None
    job_url: str | None = None
    company_logo: str | None = None
    description_preview: str | None = None
    saved_at: datetime
    is_saved: bool = True

    model_config = ConfigDict(from_attributes=True)


class SavedJobListResponse(BaseModel):
    items: list[SavedJobRead]
    total: int
    page: int
    size: int


class SavedJobStatusResponse(BaseModel):
    job_id: int | None = None
    saved_job_id: int | None = None
    is_saved: bool
