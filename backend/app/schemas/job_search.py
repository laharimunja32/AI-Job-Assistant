from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobSearchFilters(BaseModel):
    keyword: str | None = None
    location: str | None = None
    experience: str | None = None
    company: str | None = None
    salary: str | None = None
    remote: bool | None = None
    hybrid: bool | None = None
    onsite: bool | None = None
    employment_type: str | None = None
    date_posted: str | None = Field(default=None, description="e.g. today, week, month")


class JobSearchRequest(BaseModel):
    keyword: str | None = None
    location: str | None = None
    experience: str | None = None
    company: str | None = None
    salary: str | None = None
    remote: bool | None = None
    hybrid: bool | None = None
    onsite: bool | None = None
    employment_type: str | None = None
    date_posted: str | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class LiveJobResult(BaseModel):
    id: int | None = None
    title: str
    company: str
    salary: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    experience: str | None = None
    posted_date: datetime | None = None
    job_url: str | None = None
    company_logo: str | None = None
    description_preview: str | None = None
    work_mode: str | None = None


class JobSearchResponse(BaseModel):
    items: list[LiveJobResult]
    total: int
    page: int
    size: int


class JobSearchHistoryItem(BaseModel):
    id: int
    keyword: str | None = None
    location: str | None = None
    company: str | None = None
    results_count: int
    filters: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobSearchHistoryResponse(BaseModel):
    items: list[JobSearchHistoryItem]
    total: int


class JobSearchDetailResponse(BaseModel):
    id: int
    keyword: str | None = None
    location: str | None = None
    company: str | None = None
    salary: str | None = None
    experience: str | None = None
    employment_type: str | None = None
    work_mode: str | None = None
    date_posted: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    results_count: int
    page: int
    size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
