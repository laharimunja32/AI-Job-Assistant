from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResumeOptimization(Base):
    __tablename__ = "resume_optimizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ats_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    score_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    matched_keywords: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_keywords: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    matched_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    recommendations: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    tailored_resume: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    docx_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
