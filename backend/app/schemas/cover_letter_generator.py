from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GenerateCoverLetterRequest(BaseModel):
    resume_id: int
    job_description: str = Field(min_length=10)
    job_title: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    template_name: str = Field(default="professional")
    tone: str = Field(default="professional")
    length: str = Field(default="medium")


class GenerateCoverLetterResponse(BaseModel):
    id: int
    job_title: str | None = None
    company_name: str | None = None
    template_name: str
    tone: str
    length: str
    generated_letter: str


class CoverLetterHistoryItem(BaseModel):
    id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    template_name: str
    tone: str
    length: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoverLetterDetail(BaseModel):
    id: int
    user_id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    job_description: str | None = None
    template_name: str
    generated_letter: str | None = None
    tone: str
    length: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoverLetterHistoryResponse(BaseModel):
    items: list[CoverLetterHistoryItem]
    total: int
    page: int
    size: int


class CoverLetterUpdateRequest(BaseModel):
    generated_letter: str = Field(min_length=10)


class CoverLetterGeneratorStatistics(BaseModel):
    total_generated: int = 0
    generated_this_week: int = 0
    most_used_template: str | None = None


class RecentCoverLetterGeneratorItem(BaseModel):
    id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    template_name: str
    tone: str
    created_at: datetime


class LatestCoverLetterGeneratorItem(BaseModel):
    id: int
    resume_id: int
    job_title: str | None = None
    company_name: str | None = None
    template_name: str
    tone: str
    created_at: datetime
