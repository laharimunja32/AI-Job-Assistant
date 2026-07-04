from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LiveJobSearch(Base):
    """Stores live job search queries and result metadata per user."""

    __tablename__ = "live_job_searches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    keyword: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_posted: Mapped[str | None] = mapped_column(String(50), nullable=True)
    filters: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict, nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    size: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
