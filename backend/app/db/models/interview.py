from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InterviewPreparation(Base):
    """AI-generated interview preparation package for a job."""

    __tablename__ = "interview_preparations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"), nullable=True, index=True)
    tailored_resume_id: Mapped[int | None] = mapped_column(ForeignKey("tailored_resumes.id"), nullable=True, index=True)
    cover_letter_id: Mapped[int | None] = mapped_column(ForeignKey("generated_cover_letters.id"), nullable=True, index=True)
    preparation_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False, index=True)
    generation_signature: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    readiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    technical_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    behavioral_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    weaknesses: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    recommendations: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    star_examples: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, default=list, nullable=True)
    recommended_topics: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    important_topics: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    practice_recommendations: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class InterviewQuestion(Base):
    """Individual interview question linked to a preparation package."""

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    preparation_id: Mapped[int] = mapped_column(ForeignKey("interview_preparations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    follow_up_questions: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    hints: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InterviewAnswer(Base):
    """User answer submitted during a practice session."""

    __tablename__ = "interview_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("interview_questions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    improvements: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class InterviewFeedback(Base):
    """Aggregated feedback for a completed practice session."""

    __tablename__ = "interview_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"), nullable=False, index=True)
    preparation_id: Mapped[int] = mapped_column(ForeignKey("interview_preparations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    readiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    technical_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    behavioral_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    weaknesses: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    improvement_suggestions: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    important_topics: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    practice_recommendations: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    recommended_resources: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    topics_to_improve: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    score_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class InterviewSession(Base):
    """Interactive mock interview practice session."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    preparation_id: Mapped[int] = mapped_column(ForeignKey("interview_preparations.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
