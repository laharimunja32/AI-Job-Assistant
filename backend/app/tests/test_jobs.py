from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.sample_provider import SampleJobProvider
from app.services.jobs.search_service import JobSearchService
from app.db.models.job import Job


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def test_job_parser_normalizes_payload() -> None:
    parser = JobParserService()
    payload = {
        "title": "Python Backend Engineer",
        "company": "Example Labs",
        "location": "Hyderabad",
        "description": "Build APIs with FastAPI and PostgreSQL",
        "skills": ["Python", "FastAPI"],
        "experience": "0-2 years",
        "employment_type": "Full Time",
        "work_mode": "Remote",
        "salary": "12-18 LPA",
        "apply_url": "https://example.com/jobs/1",
        "source": "sample",
        "posted_date": "2026-07-01",
        "tags": ["fresher", "remote"],
    }

    result = parser.parse_job_payload(payload)

    assert result["title"] == "Python Backend Engineer"
    assert result["company"] == "Example Labs"
    assert result["location"] == "Hyderabad"
    assert result["work_mode"] == "Remote"
    assert result["skills"] == ["Python", "FastAPI"]


def test_duplicate_detection_identifies_matching_jobs() -> None:
    detector = DuplicateDetectionService()
    existing_job = Job(
        title="Python Backend Engineer",
        company_name="Example Labs",
        location="Hyderabad",
        description="Build APIs with FastAPI and PostgreSQL",
        source_name="sample",
        apply_url="https://example.com/jobs/1",
    )

    candidate = {
        "title": "Python Backend Engineer",
        "company": "Example Labs",
        "location": "Hyderabad",
        "description": "Build APIs with FastAPI and PostgreSQL",
        "source": "sample",
        "apply_url": "https://example.com/jobs/1",
    }

    assert detector.is_duplicate(existing_job, candidate) is True


def test_search_service_persists_and_filters_jobs() -> None:
    db = TestingSessionLocal()
    provider = SampleJobProvider()
    service = JobSearchService(
        db=db,
        providers=[provider],
        parser=JobParserService(),
        duplicate_detector=DuplicateDetectionService(),
    )

    result = service.search_jobs(keyword="python", location="Hyderabad")

    assert result["total"] >= 1
    assert result["items"][0]["title"].startswith("Python")
    assert result["items"][0]["location"] == "Hyderabad"

    db.close()
