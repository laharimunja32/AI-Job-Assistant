from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EducationItem(BaseModel):
    institution: str | None = Field(default=None, description="Institution name")
    degree: str | None = Field(default=None, description="Degree or diploma")
    field: str | None = Field(default=None, description="Field of study")
    start_date: str | None = Field(default=None, description="Start date")
    end_date: str | None = Field(default=None, description="End date")
    description: str | None = Field(default=None, description="Additional details")


class CertificationItem(BaseModel):
    name: str | None = Field(default=None, description="Certification name")
    issuer: str | None = Field(default=None, description="Issuing organization")
    issued_date: str | None = Field(default=None, description="Issue date")
    expires_at: str | None = Field(default=None, description="Expiry date")


class ProjectItem(BaseModel):
    name: str | None = Field(default=None, description="Project name")
    description: str | None = Field(default=None, description="Project summary")
    url: str | None = Field(default=None, description="Project URL")


class WorkPreferences(BaseModel):
    remote: bool | None = Field(default=None, description="Open to remote roles")
    relocation: bool | None = Field(default=None, description="Open to relocation")
    availability: str | None = Field(default=None, description="Availability timeline")


class ProfileBase(BaseModel):
    full_name: str | None = Field(default=None, description="User full name")
    phone: str | None = Field(default=None, description="Phone number")
    address: str | None = Field(default=None, description="Street address")
    location: str | None = Field(default=None, description="Current city or region")
    education: list[EducationItem] | None = Field(default=None, description="Educational background")
    skills: list[str] | None = Field(default=None, description="Professional skills")
    certifications: list[CertificationItem] | None = Field(default=None, description="Professional certifications")
    projects: list[ProjectItem] | None = Field(default=None, description="Projects")
    work_preferences: WorkPreferences | None = Field(default=None, description="Work preference settings")
    preferred_job_roles: list[str] | None = Field(default=None, description="Preferred job roles")
    preferred_locations: list[str] | None = Field(default=None, description="Preferred work locations")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    github_url: str | None = Field(default=None, description="GitHub profile URL")
    portfolio_url: str | None = Field(default=None, description="Portfolio URL")


class ProfileCreateUpdate(ProfileBase):
    """Schema for creating or updating a user profile."""


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    email: str | None = Field(default=None, description="User email address")
    skills: list[str] = Field(default_factory=list, description="Professional skills")
    education: list[EducationItem] = Field(default_factory=list, description="Educational background")
    certifications: list[CertificationItem] = Field(default_factory=list, description="Professional certifications")
    projects: list[ProjectItem] = Field(default_factory=list, description="Projects")
    preferred_job_roles: list[str] = Field(default_factory=list, description="Preferred job roles")
    preferred_locations: list[str] = Field(default_factory=list, description="Preferred work locations")
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)
