from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AggregationRun(Base):
    """Records execution history and statistics for background aggregation jobs."""

    __tablename__ = "aggregation_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="running", nullable=False)
    providers_attempted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    providers_succeeded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    providers_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_expired: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    walk_ins_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    walk_ins_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicates_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, default=list, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
