"""Lightweight schema patches for existing databases without Alembic."""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.core.config import settings

_INTERVIEW_FEEDBACK_COLUMNS: dict[str, str] = {
    "grammar_score": "FLOAT",
    "clarity_score": "FLOAT",
    "problem_solving_score": "FLOAT",
    "summary_feedback": "TEXT",
}


def apply_schema_patches(engine: Engine) -> None:
    """Add nullable columns introduced after initial table creation."""
    inspector = inspect(engine)
    if not inspector.has_table("interview_feedback"):
        return

    existing = {column["name"] for column in inspector.get_columns("interview_feedback")}
    pending = {
        name: col_type for name, col_type in _INTERVIEW_FEEDBACK_COLUMNS.items() if name not in existing
    }
    if not pending:
        return

    with engine.begin() as connection:
        for name, col_type in pending.items():
            if settings.database_url.startswith("sqlite"):
                connection.execute(text(f"ALTER TABLE interview_feedback ADD COLUMN {name} {col_type}"))
            else:
                connection.execute(
                    text(f"ALTER TABLE interview_feedback ADD COLUMN IF NOT EXISTS {name} {col_type}")
                )
