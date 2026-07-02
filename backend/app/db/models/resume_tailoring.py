from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResumeTemplate(Base):
    """Snapshot of the source resume/profile context used for tailoring."""

    __tablename__ = "resume_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id"), nullable=True, index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("profiles.id"), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_resume_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TailoredResume(Base):
    """Generated resume versions tailored for a specific job."""

    __tablename__ = "tailored_resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("resume_templates.id"), nullable=True, index=True)
    match_id: Mapped[int | None] = mapped_column(ForeignKey("job_matches.id"), nullable=True, index=True)
    resume_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    generation_signature: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    improvements: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    markdown_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    markdown_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    html_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    docx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ResumeGenerationHistory(Base):
    """Tracks generation lifecycle events for observability and dashboard history."""

    __tablename__ = "resume_generation_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tailored_resume_id: Mapped[int | None] = mapped_column(ForeignKey("tailored_resumes.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
