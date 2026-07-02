from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CoverLetterAnalysis(BaseModel):
    company_name: str = ""
    role: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    company_values: list[str] = Field(default_factory=list)
    industry: str | None = None
    keywords: list[str] = Field(default_factory=list)


class CoverLetterSections(BaseModel):
    introduction: str = ""
    role_interest: str = ""
    relevant_skills: list[str] = Field(default_factory=list)
    relevant_projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    closing_paragraph: str = ""
    professional_signature: str = ""


class CoverLetterTemplateBase(BaseModel):
    name: str
    intro_style: str | None = None
    closing_style: str | None = None
    body_guidance: str | None = None
    signature_block: str | None = None
    is_default: bool = False


class CoverLetterTemplateCreate(CoverLetterTemplateBase):
    pass


class CoverLetterTemplateUpdate(BaseModel):
    name: str | None = None
    intro_style: str | None = None
    closing_style: str | None = None
    body_guidance: str | None = None
    signature_block: str | None = None
    is_default: bool | None = None


class CoverLetterTemplateRead(CoverLetterTemplateBase):
    id: int
    user_id: int
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GeneratedCoverLetterRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    company_name: str | None = None
    template_id: int | None = None
    resume_id: int | None = None
    tailored_resume_id: int | None = None
    match_id: int | None = None
    cover_letter_version: int
    status: str
    download_formats: list[str] = Field(default_factory=list)
    analysis: CoverLetterAnalysis = Field(default_factory=CoverLetterAnalysis)
    sections: CoverLetterSections = Field(default_factory=CoverLetterSections)
    markdown_content: str | None = None
    html_content: str | None = None
    quality_score: float | None = None
    generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoverLetterGenerateResponse(BaseModel):
    cover_letter_id: int
    status: str
    cached: bool = False
    message: str


class CoverLetterHistoryItem(BaseModel):
    id: int
    generated_cover_letter_id: int | None = None
    user_id: int
    job_id: int
    company_name: str | None = None
    status: str
    message: str | None = None
    retry_count: int
    quality_score: float | None = None
    generated_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoverLetterHistoryResponse(BaseModel):
    items: list[CoverLetterHistoryItem]
    total: int
    page: int
    size: int
