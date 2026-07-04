from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeOptimizerAnalyzeRequest(BaseModel):
    resume_id: int
    job_description: str = Field(min_length=10)
    job_title: str | None = None
    company_name: str | None = None


class ScoreBreakdown(BaseModel):
    ats_score: float
    keyword_match: float
    skill_match: float
    experience_match: float
    education_match: float
    overall_score: float


class ResumeOptimizerAnalyzeResponse(BaseModel):
    id: int
    ats_score: float
    overall_score: float
    keyword_match: float
    skill_match: float
    experience_match: float
    education_match: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    tailored_resume: str


class ResumeOptimizationRead(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    ats_score: float
    overall_score: float
    keyword_match: float
    skill_match: float
    experience_match: float
    education_match: float
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    tailored_resume: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeOptimizationHistoryItem(BaseModel):
    id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    ats_score: float
    overall_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeOptimizationHistoryResponse(BaseModel):
    items: list[ResumeOptimizationHistoryItem]
    total: int
    page: int
    size: int
