from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WalkInEvent(Base):
    """Represents a walk-in drive event discovered from providers."""

    __tablename__ = "walk_in_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_role: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    venue: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(255), nullable=True)
    walk_in_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    walk_in_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    registration_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    eligibility: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(255), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passout_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    experience_required: Mapped[str | None] = mapped_column(String(100), nullable=True)
    documents_required: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    contact_details: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    registration_url: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    event_status: Mapped[str] = mapped_column(String(50), default="Upcoming", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
