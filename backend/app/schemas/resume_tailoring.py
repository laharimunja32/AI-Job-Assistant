from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeAnalysis(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    experience: str | None = None
    keywords: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


class ResumeImprovements(BaseModel):
    professional_summary: str = ""
    skills_ordering: list[str] = Field(default_factory=list)
    relevant_projects: list[str] = Field(default_factory=list)
    relevant_certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    keyword_optimization: list[str] = Field(default_factory=list)
    ats_optimization: list[str] = Field(default_factory=list)


class TailoredResumeRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    template_id: int | None = None
    match_id: int | None = None
    resume_version: int
    status: str
    generated_at: datetime | None = None
    ats_score: float | None = None
    analysis: ResumeAnalysis = Field(default_factory=ResumeAnalysis)
    improvements: ResumeImprovements = Field(default_factory=ResumeImprovements)
    markdown_content: str | None = None
    html_content: str | None = None
    markdown_path: str | None = None
    html_path: str | None = None
    pdf_path: str | None = None
    docx_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TailoredResumeGenerateResponse(BaseModel):
    tailored_resume_id: int
    status: str
    cached: bool = False
    message: str


class ResumeGenerationHistoryItem(BaseModel):
    id: int
    tailored_resume_id: int | None = None
    user_id: int
    job_id: int
    status: str
    message: str | None = None
    ats_score: float | None = None
    generated_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeGenerationHistoryResponse(BaseModel):
    items: list[ResumeGenerationHistoryItem]
    total: int
    page: int
    size: int
