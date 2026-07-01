from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    title: str = Field(..., description="Job title")
    company: str | None = Field(default=None, description="Company name")
    description: str | None = Field(default=None, description="Job description")
    skills: list[str] | None = Field(default=None, description="Required skills")
    experience: str | None = Field(default=None, description="Experience level")
    education: list[str] | None = Field(default=None, description="Education requirements")
    employment_type: str | None = Field(default=None, description="Employment type")
    work_mode: str | None = Field(default=None, description="Remote, hybrid, or onsite")
    location: str | None = Field(default=None, description="Job location")
    salary: str | None = Field(default=None, description="Salary details")
    apply_url: str | None = Field(default=None, description="Application URL")
    source: str | None = Field(default=None, description="Job source name")
    posted_date: datetime | None = Field(default=None, description="Original posting date")
    last_updated: datetime | None = Field(default=None, description="Last updated date")
    status: str | None = Field(default="active", description="Job status")
    tags: list[str] | None = Field(default=None, description="Tags for categorization")
    external_id: str | None = Field(default=None, description="External provider identifier")


class JobCreateUpdate(JobBase):
    pass


class JobRead(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: list[JobRead]
    total: int
    page: int
    size: int
