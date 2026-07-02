from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MatchRead(BaseModel):
    id: int | None = Field(default=None, description="Persisted match identifier")
    job_id: int | None = Field(default=None, description="Matched job identifier")
    user_id: int | None = Field(default=None, description="User identifier")
    score: int = Field(default=0, description="Overall match score out of 100")
    category: str = Field(default="Weak Match", description="Display category for the score")
    matched_skills: list[str] = Field(default_factory=list, description="Skills shared with the job")
    missing_skills: list[str] = Field(default_factory=list, description="Skills the candidate should add")
    missing_certifications: list[str] = Field(default_factory=list, description="Certifications that would strengthen the match")
    missing_technologies: list[str] = Field(default_factory=list, description="Technology gaps surfaced by the analysis")
    location_compatible: bool = Field(default=False, description="Whether the location matches the job")
    experience_compatible: bool = Field(default=False, description="Whether the experience level fits")
    reasoning: str = Field(default="", description="Summary of why the job was scored this way")
    profile_improvements: list[str] = Field(default_factory=list, description="Suggested profile improvements")
    resume_improvements: list[str] = Field(default_factory=list, description="Suggested resume improvements")
    created_at: datetime | None = Field(default=None, description="When the match was computed")

    model_config = ConfigDict(from_attributes=True)


class MatchHistoryResponse(BaseModel):
    items: list[MatchRead]
    total: int
    page: int
    size: int
