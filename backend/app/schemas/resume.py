from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeBase(BaseModel):
    filename: str = Field(..., description="Original file name")
    content_type: str = Field(..., description="Uploaded file content type")
    file_size: int = Field(..., description="File size in bytes")
    version: int = Field(default=1, description="Resume version number")
    is_active: bool = Field(default=True, description="Whether this is the active resume")
    metadata: dict | None = Field(default=None, description="Additional file metadata", alias="file_metadata")


class ResumeRead(ResumeBase):
    id: int
    user_id: int
    storage_path: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ResumeListResponse(BaseModel):
    items: list[ResumeRead]
    total: int
    page: int
    size: int
