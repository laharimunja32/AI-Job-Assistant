from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SubmissionReviewAudit(Base):
    __tablename__ = "submission_review_audits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("browser_sessions.session_id"), nullable=False, index=True)
    review_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    validation_results: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    user_confirmation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    submission_attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    result: Mapped[str] = mapped_column(String(40), default="review_recorded", nullable=False, index=True)
    browser_session_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    current_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    warnings: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    errors: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
