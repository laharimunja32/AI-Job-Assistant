from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WalkInBase(BaseModel):
    company_name: str = Field(..., description="Company hosting the walk-in drive")
    job_role: str = Field(..., description="Role being recruited")
    job_description: str | None = Field(default=None, description="Role and event description")
    venue: str | None = Field(default=None, description="Walk-in venue")
    city: str | None = Field(default=None, description="City")
    state: str | None = Field(default=None, description="State")
    walk_in_date: date | None = Field(default=None, description="Date of the walk-in drive")
    walk_in_time: str | None = Field(default=None, description="Time of the walk-in drive")
    registration_deadline: date | None = Field(default=None, description="Last date to register")
    eligibility: str | None = Field(default=None, description="Eligibility criteria")
    degree: str | None = Field(default=None, description="Required degree")
    branch: str | None = Field(default=None, description="Eligible branches")
    passout_year: str | None = Field(default=None, description="Eligible passout years")
    skills: list[str] | None = Field(default=None, description="Required skills")
    experience_required: str | None = Field(default=None, description="Experience requirement")
    documents_required: list[str] | None = Field(default=None, description="Documents to carry")
    contact_details: str | None = Field(default=None, description="Contact information")
    registration_url: str | None = Field(default=None, description="Registration or apply URL")
    source: str | None = Field(default=None, description="Discovery source")
    event_status: str = Field(default="Upcoming", description="Upcoming, Today, Completed, or Cancelled")


class WalkInRead(WalkInBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalkInListResponse(BaseModel):
    items: list[WalkInRead]
    total: int
    page: int
    size: int


class WalkInRefreshResponse(BaseModel):
    created: int
    updated: int
    total: int
