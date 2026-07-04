from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.migrations import apply_schema_patches
from app.db.models import Company, Job, JobSource, Profile, Resume, SearchHistory, User, WalkInEvent  # noqa: F401  Import for model registration
from app.db.models.aggregation import AggregationRun  # noqa: F401  Import for model registration
from app.db.models.application import Application, ApplicationHistory  # noqa: F401  Import for model registration
from app.db.models.cover_letter import CoverLetterGenerationHistory, CoverLetterTemplate, GeneratedCoverLetter  # noqa: F401  Import for model registration
from app.db.models.cover_letter_generator import CoverLetter  # noqa: F401  Import for model registration
from app.db.models.browser_session import BrowserSession  # noqa: F401  Import for model registration
from app.db.models.interview import (  # noqa: F401  Import for model registration
    InterviewAnswer,
    InterviewFeedback,
    InterviewPreparation,
    InterviewQuestion,
    InterviewSession,
)
from app.db.models.recruitment_monitoring import Assessment, EmailEvent, Interview, NotificationHistory, Reminder, TimelineEvent  # noqa: F401  Import for model registration
from app.db.models.submission_review import SubmissionReviewAudit  # noqa: F401  Import for model registration
from app.db.models.resume_optimization import ResumeOptimization  # noqa: F401  Import for model registration
from app.db.models.resume_tailoring import ResumeGenerationHistory, ResumeTemplate, TailoredResume  # noqa: F401  Import for model registration
from app.services.jobs.match_service import JobMatch  # noqa: F401  Import for model registration

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, echo=settings.db_echo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Create database tables for all registered models."""
    Base.metadata.create_all(bind=engine)
    apply_schema_patches(engine)


def get_db():
    """Provide a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
