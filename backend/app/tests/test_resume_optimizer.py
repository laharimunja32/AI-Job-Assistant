from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.resume_optimization import ResumeOptimization  # noqa: F401
from app.db.models.user import User
from app.db.session import get_db
from app.services.resume_optimizer_service import ResumeOptimizerService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()
app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _seed(db, email: str = "optimizer@example.com"):
    user = User(email=email, hashed_password="hash", full_name="Optimizer User")
    db.add(user)
    db.flush()
    db.add(
        Profile(
            user_id=user.id,
            location="Hyderabad",
            skills=["Python", "FastAPI", "SQL", "Docker"],
            education=[{"degree": "B.Tech Computer Science", "institution": "State University"}],
            certifications=[{"name": "AWS Certified Developer"}],
            projects=[{"name": "API Platform", "description": "Built REST APIs with Python and FastAPI"}],
        )
    )
    resume = Resume(
        user_id=user.id,
        filename="master_resume.pdf",
        content_type="application/pdf",
        file_size=1024,
        storage_path=str((Path(__file__).resolve().parents[3] / "uploads" / "resumes" / "test_resume.txt")),
        is_active=True,
        file_metadata={
            "content": "Python developer with 3 years experience. Built REST APIs using FastAPI and SQL. Deployed with Docker on AWS.",
            "experience_years": 3,
        },
    )
    db.add(resume)
    db.commit()
    db.refresh(user)
    db.refresh(resume)
    return user, resume


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(subject=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def test_analyze_resume_optimization():
    db = TestingSessionLocal()
    user, resume = _seed(db)
    headers = _auth_headers(user)
    job_description = (
        "Backend Engineer at Acme Corp. Requirements: Python, FastAPI, SQL, Docker, AWS. "
        "3+ years experience. Bachelor's degree in Computer Science required."
    )
    response = client.post(
        "/api/v1/resume-optimizer/analyze",
        headers=headers,
        json={"resume_id": resume.id, "job_description": job_description, "job_title": "Backend Engineer", "company_name": "Acme"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ats_score"] >= 0
    assert data["overall_score"] >= 0
    assert "Python" in data["matched_skills"] or "Fastapi" in [s.title() for s in data["matched_skills"]]
    assert isinstance(data["matched_keywords"], list)
    assert isinstance(data["recommendations"], list)
    assert len(data["tailored_resume"]) > 50
    assert "React" not in data["tailored_resume"] or "react" in resume.file_metadata["content"].lower()
    db.close()


def test_optimization_history_and_detail():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="optimizer2@example.com")
    headers = _auth_headers(user)
    job_description = "Senior Python Engineer. Skills: Python, Kubernetes, Terraform. 5+ years. Master's preferred."

    analyze = client.post(
        "/api/v1/resume-optimizer/analyze",
        headers=headers,
        json={"resume_id": resume.id, "job_description": job_description},
    )
    assert analyze.status_code == 200
    analysis_id = analyze.json()["id"]

    history = client.get("/api/v1/resume-optimizer/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 1

    detail = client.get(f"/api/v1/resume-optimizer/{analysis_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["id"] == analysis_id
    assert detail.json()["keyword_match"] >= 0
    db.close()


def test_delete_optimization():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="optimizer3@example.com")
    headers = _auth_headers(user)
    analyze = client.post(
        "/api/v1/resume-optimizer/analyze",
        headers=headers,
        json={"resume_id": resume.id, "job_description": "Data Analyst role requiring Python, SQL, and Excel skills."},
    )
    analysis_id = analyze.json()["id"]
    deleted = client.delete(f"/api/v1/resume-optimizer/{analysis_id}", headers=headers)
    assert deleted.status_code == 204
    missing = client.get(f"/api/v1/resume-optimizer/{analysis_id}", headers=headers)
    assert missing.status_code == 404
    db.close()


def test_download_optimized_resume():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="optimizer4@example.com")
    headers = _auth_headers(user)
    analyze = client.post(
        "/api/v1/resume-optimizer/analyze",
        headers=headers,
        json={"resume_id": resume.id, "job_description": "Python backend role with FastAPI, SQL, and Docker requirements."},
    )
    analysis_id = analyze.json()["id"]
    pdf = client.get(f"/api/v1/resume-optimizer/{analysis_id}/download?format=pdf", headers=headers)
    assert pdf.status_code == 200
    assert len(pdf.content) > 0
    docx = client.get(f"/api/v1/resume-optimizer/{analysis_id}/download?format=docx", headers=headers)
    assert docx.status_code == 200
    db.close()


def test_service_does_not_invent_skills():
    db = TestingSessionLocal()
    user, resume = _seed(db, email="optimizer5@example.com")
    service = ResumeOptimizerService(db)
    result = service.analyze(
        user,
        resume.id,
        "Looking for expert in Rust, Haskell, and Erlang with 10 years experience.",
    )
    tailored = result["tailored_resume"].lower()
    assert "haskell" not in tailored
    assert "erlang" not in tailored
    assert "rust" not in tailored.split("## core skills")[1] if "## core skills" in tailored else True
    db.close()


def test_analyze_missing_resume():
    db = TestingSessionLocal()
    user, _ = _seed(db, email="optimizer6@example.com")
    headers = _auth_headers(user)
    response = client.post(
        "/api/v1/resume-optimizer/analyze",
        headers=headers,
        json={"resume_id": 99999, "job_description": "Some job description with enough text to pass validation."},
    )
    assert response.status_code == 404
    db.close()
