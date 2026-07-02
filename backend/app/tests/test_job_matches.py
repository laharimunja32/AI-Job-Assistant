from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.services.jobs.match_service import JobMatchService


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def test_job_match_service_calculates_score_and_suggestions() -> None:
    db = TestingSessionLocal()
    try:
        user = User(email="matcher@example.com", hashed_password="hash", full_name="Jane Doe")
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            location="Hyderabad",
            skills=["Python", "FastAPI", "PostgreSQL"],
            certifications=[{"name": "AWS Cloud Practitioner", "issuer": "AWS"}],
            projects=[{"name": "API platform", "description": "Built FastAPI service"}],
            education=[{"degree": "B.Tech", "field": "Computer Science"}],
            preferred_locations=["Remote", "Hyderabad"],
            work_preferences={"remote": True, "relocation": False},
        )
        db.add(profile)

        resume = Resume(
            user_id=user.id,
            filename="jane_resume.pdf",
            content_type="application/pdf",
            file_size=1234,
            storage_path="/tmp/jane_resume.pdf",
            is_active=True,
            file_metadata={"experience_years": 2},
        )
        db.add(resume)

        job = Job(
            title="Backend Engineer",
            company_name="Acme",
            description="Build APIs with Python, FastAPI, PostgreSQL and AWS.",
            skills=["Python", "FastAPI", "PostgreSQL", "AWS"],
            experience="0-2 years",
            education=["Bachelor's Degree"],
            location="Remote",
            employment_type="Full Time",
            work_mode="Remote",
            tags=["backend", "python"],
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        service = JobMatchService(db=db)
        match = service.match_job(job.id, user)

        assert 0 <= match.score <= 100
        assert match.category in {"Excellent Match", "Strong Match", "Good Match", "Moderate Match", "Weak Match"}
        assert "Python" in match.matched_skills
        assert "AWS" in match.missing_skills or "AWS" in match.missing_technologies
        assert match.reasoning
        assert match.profile_improvements
    finally:
        db.close()


def test_job_match_history_can_be_filtered() -> None:
    db = TestingSessionLocal()
    try:
        user = User(email="matcher2@example.com", hashed_password="hash", full_name="John Doe")
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            location="Bengaluru",
            skills=["Python"],
            certifications=[],
            projects=[],
            education=[],
            preferred_locations=["Bengaluru"],
            work_preferences={"remote": False, "relocation": True},
        )
        db.add(profile)
        db.commit()

        first_job = Job(title="Data Engineer", company_name="X", description="Python and SQL work", skills=["Python", "SQL"], location="Bengaluru", experience="0-2 years")
        second_job = Job(title="ML Engineer", company_name="Y", description="Python and PyTorch", skills=["Python", "PyTorch"], location="Remote", experience="2-4 years")
        db.add_all([first_job, second_job])
        db.commit()

        service = JobMatchService(db=db)
        service.match_job(first_job.id, user)
        service.match_job(second_job.id, user)

        history = service.get_match_history(user, min_score=30)

        assert history["total"] >= 2
        assert history["items"]
    finally:
        db.close()
