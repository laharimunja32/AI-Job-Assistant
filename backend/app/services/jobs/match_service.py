from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User


@dataclass
class MatchResult:
    id: int | None = None
    job_id: int | None = None
    user_id: int | None = None
    score: int = 0
    category: str = "Weak Match"
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    missing_certifications: list[str] = field(default_factory=list)
    missing_technologies: list[str] = field(default_factory=list)
    location_compatible: bool = False
    experience_compatible: bool = False
    reasoning: str = ""
    profile_improvements: list[str] = field(default_factory=list)
    resume_improvements: list[str] = field(default_factory=list)
    created_at: datetime | None = None


class JobMatchService:
    """Calculate a structured compatibility score between a user profile and a job."""

    def __init__(self, db: Session):
        self.db = db
        self._cache: dict[tuple[int, int], MatchResult] = {}

    def match_job(self, job_id: int, user: User) -> MatchResult:
        cache_key = (user.id, job_id)
        if cache_key in self._cache:
            return self._cache[cache_key]

        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise ValueError("Job not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        resume = self.db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active.is_(True)).order_by(Resume.version.desc()).first()

        profile_data = self._profile_payload(profile)
        resume_data = self._resume_payload(resume)
        match = self._build_match_result(job, profile_data, resume_data)
        self._persist_match(job, user, match)
        self._cache[cache_key] = match
        return match

    def match_all_jobs(self, user: User) -> list[MatchResult]:
        jobs = self.db.query(Job).filter(Job.status == "active").all()
        return [self.match_job(job.id, user) for job in jobs]

    def get_match_history(self, user: User, min_score: int | None = None, page: int = 1, size: int = 20) -> dict[str, Any]:
        matches = self.db.query(JobMatch).filter(JobMatch.user_id == user.id)
        if min_score is not None:
            matches = matches.filter(JobMatch.score >= min_score)

        total = matches.count()
        items = matches.order_by(JobMatch.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {
            "items": [self._serialize_match(match) for match in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def recalculate_match(self, match_id: int, user: User) -> MatchResult:
        stored = self.db.query(JobMatch).filter(JobMatch.id == match_id, JobMatch.user_id == user.id).first()
        if stored is None:
            raise ValueError("Match not found")

        job = self.db.query(Job).filter(Job.id == stored.job_id).first()
        if job is None:
            raise ValueError("Job not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        resume = self.db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active.is_(True)).order_by(Resume.version.desc()).first()

        match = self._build_match_result(job, self._profile_payload(profile), self._resume_payload(resume))
        stored.score = match.score
        stored.category = match.category
        stored.matched_skills = match.matched_skills
        stored.missing_skills = match.missing_skills
        stored.missing_certifications = match.missing_certifications
        stored.missing_technologies = match.missing_technologies
        stored.location_compatible = match.location_compatible
        stored.experience_compatible = match.experience_compatible
        stored.reasoning = match.reasoning
        stored.profile_improvements = match.profile_improvements
        stored.resume_improvements = match.resume_improvements
        stored.created_at = datetime.utcnow()
        self.db.add(stored)
        self.db.commit()
        self.db.refresh(stored)
        return self._serialize_match(stored)

    def _build_match_result(self, job: Job, profile_data: dict[str, Any], resume_data: dict[str, Any]) -> MatchResult:
        profile_skills = {self._normalize_term(skill) for skill in profile_data.get("skills", []) if isinstance(skill, str)}
        job_skills = [skill for skill in (job.skills or []) if isinstance(skill, str)]
        job_skill_norms = {self._normalize_term(skill): skill for skill in job_skills}
        matched_skills = [job_skill_norms[norm] for norm in sorted(profile_skills & set(job_skill_norms))]
        missing_skills = [job_skill_norms[norm] for norm in sorted(set(job_skill_norms) - profile_skills)]

        profile_tech = {self._normalize_term(item) for item in profile_data.get("technologies", []) if isinstance(item, str)}
        job_tech_terms = self._extract_technologies(job)
        job_tech_norms = {self._normalize_term(item): item for item in job_tech_terms}
        matched_tech = [job_tech_norms[norm] for norm in sorted(profile_tech & set(job_tech_norms))]
        missing_tech = [job_tech_norms[norm] for norm in sorted(set(job_tech_norms) - profile_tech)]

        profile_certs = {self._normalize_term(str(item.get("name", ""))) for item in profile_data.get("certifications", []) if isinstance(item, dict)}
        job_certs = {self._normalize_term(item) for item in (job.tags or []) if isinstance(item, str)}
        missing_certs = [cert for cert in sorted(job_certs - profile_certs)] if job_certs else []

        location_compatible = self._is_location_compatible(job, profile_data)
        experience_compatible = self._is_experience_compatible(job, resume_data)

        skill_score = min(70, max(30, len(matched_skills) * 20))
        tech_score = min(20, len(matched_tech) * 5)
        location_score = 10 if location_compatible else 0
        experience_score = 10 if experience_compatible else 0
        cert_score = min(10, max(0, 10 - len(missing_certs) * 2)) if job_certs else 0
        total = min(100, skill_score + tech_score + location_score + experience_score + cert_score)

        if total >= 90:
            category = "Excellent Match"
        elif total >= 80:
            category = "Strong Match"
        elif total >= 70:
            category = "Good Match"
        elif total >= 60:
            category = "Moderate Match"
        else:
            category = "Weak Match"

        reasoning = self._build_reasoning(job, matched_skills, missing_skills, missing_certs, missing_tech, location_compatible, experience_compatible, total)
        profile_improvements = self._build_profile_improvements(missing_skills, missing_certs, missing_tech)
        resume_improvements = self._build_resume_improvements(missing_skills, missing_tech)

        return MatchResult(
            score=total,
            category=category,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            missing_certifications=missing_certs,
            missing_technologies=missing_tech,
            location_compatible=location_compatible,
            experience_compatible=experience_compatible,
            reasoning=reasoning,
            profile_improvements=profile_improvements,
            resume_improvements=resume_improvements,
        )

    def _persist_match(self, job: Job, user: User, match: MatchResult) -> None:
        existing = self.db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id).first()
        if existing is None:
            stored = JobMatch(
                job_id=job.id,
                user_id=user.id,
                score=match.score,
                category=match.category,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                missing_certifications=match.missing_certifications,
                missing_technologies=match.missing_technologies,
                location_compatible=match.location_compatible,
                experience_compatible=match.experience_compatible,
                reasoning=match.reasoning,
                profile_improvements=match.profile_improvements,
                resume_improvements=match.resume_improvements,
            )
            self.db.add(stored)
            self.db.commit()
            self.db.refresh(stored)
            return

        existing.score = match.score
        existing.category = match.category
        existing.matched_skills = match.matched_skills
        existing.missing_skills = match.missing_skills
        existing.missing_certifications = match.missing_certifications
        existing.missing_technologies = match.missing_technologies
        existing.location_compatible = match.location_compatible
        existing.experience_compatible = match.experience_compatible
        existing.reasoning = match.reasoning
        existing.profile_improvements = match.profile_improvements
        existing.resume_improvements = match.resume_improvements
        self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)

    def _profile_payload(self, profile: Profile | None) -> dict[str, Any]:
        if profile is None:
            return {"skills": [], "certifications": [], "technologies": [], "location": None, "work_preferences": {}}
        return {
            "skills": profile.skills or [],
            "certifications": profile.certifications or [],
            "technologies": self._extract_profile_technologies(profile),
            "location": profile.location,
            "work_preferences": profile.work_preferences or {},
        }

    def _resume_payload(self, resume: Resume | None) -> dict[str, Any]:
        if resume is None:
            return {"experience_years": 0, "technologies": []}
        metadata = resume.file_metadata or {}
        experience_years = metadata.get("experience_years", 0)
        return {
            "experience_years": experience_years,
            "technologies": self._extract_resume_technologies(resume),
        }

    def _extract_profile_technologies(self, profile: Profile) -> list[str]:
        technologies: set[str] = set()
        if profile.skills:
            technologies.update(profile.skills)
        if profile.projects:
            for project in profile.projects:
                description = (project or {}).get("description", "")
                technologies.update(self._extract_keywords(description))
        return sorted(technologies)

    def _extract_resume_technologies(self, resume: Resume) -> list[str]:
        if not resume:
            return []
        metadata = resume.file_metadata or {}
        content = metadata.get("content", "")
        if isinstance(content, str):
            return self._extract_keywords(content)
        return []

    def _extract_technologies(self, job: Job) -> list[str]:
        technologies = list(job.skills or [])
        if job.tags:
            technologies.extend(job.tags or [])
        if job.description:
            description_terms = [term for term in self._extract_keywords(job.description) if term.lower() not in self._common_noise_words()]
            technologies.extend(description_terms)
        return sorted(set(technologies))

    def _extract_keywords(self, text: str) -> list[str]:
        return [item.strip() for item in re.split(r"[^A-Za-z0-9+#.]+", text) if item.strip()]

    def _normalize_term(self, term: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(term).lower())

    def _common_noise_words(self) -> set[str]:
        return {"and", "the", "for", "with", "build", "apis", "role", "work", "backend", "engineer"}

    def _is_location_compatible(self, job: Job, profile_data: dict[str, Any]) -> bool:
        if not job.location:
            return True
        if not profile_data.get("location"):
            return False
        job_location = job.location.lower()
        profile_location = str(profile_data.get("location", "")).lower()
        if profile_location in job_location or job_location in profile_location:
            return True
        preferred_locations = profile_data.get("work_preferences", {}).get("preferred_locations", []) if isinstance(profile_data.get("work_preferences"), dict) else []
        return any(location.lower() in job_location or job_location in location.lower() for location in preferred_locations)

    def _is_experience_compatible(self, job: Job, resume_data: dict[str, Any]) -> bool:
        if not job.experience:
            return True
        years = resume_data.get("experience_years", 0)
        if isinstance(years, str):
            try:
                years = int(years)
            except ValueError:
                return True

        experience_text = str(job.experience).lower()
        if "0-2" in experience_text or "fresher" in experience_text or "junior" in experience_text:
            return years <= 2
        if "2-4" in experience_text or "mid" in experience_text:
            return years >= 2
        if "4+" in experience_text or "senior" in experience_text:
            return years >= 4
        return years >= 0

    def _build_reasoning(self, job: Job, matched_skills: list[str], missing_skills: list[str], missing_certs: list[str], missing_tech: list[str], location_compatible: bool, experience_compatible: bool, total: int) -> str:
        details = [f"Your profile aligns with {job.title} based on {', '.join(matched_skills[:3]) or 'the role requirements'}."]
        if missing_skills:
            details.append(f"The main gaps are {', '.join(missing_skills[:3])}.")
        if not location_compatible:
            details.append("Location preference does not align well with the posting.")
        if not experience_compatible:
            details.append("The experience profile may need a stronger match for this role.")
        if missing_certs:
            details.append("Certifications are a notable gap for this opportunity.")
        return " ".join(details) + f" Overall score: {total}/100."

    def _build_profile_improvements(self, missing_skills: list[str], missing_certs: list[str], missing_tech: list[str]) -> list[str]:
        improvements = []
        if missing_skills:
            improvements.append(f"Add experience with {', '.join(missing_skills[:3])} to your profile.")
        if missing_certs:
            improvements.append("Add the missing certifications to your profile.")
        if missing_tech:
            improvements.append(f"Highlight projects that use {', '.join(missing_tech[:3])}.")
        return improvements or ["Keep your profile current and add recent project outcomes."]

    def _build_resume_improvements(self, missing_skills: list[str], missing_tech: list[str]) -> list[str]:
        improvements = []
        if missing_skills:
            improvements.append(f"Emphasize your experience with {', '.join(missing_skills[:3])} in the resume.")
        if missing_tech:
            improvements.append(f"Mention tooling such as {', '.join(missing_tech[:3])} in the resume.")
        return improvements or ["Refine the summary and achievements section to mirror the target role."]

    def _serialize_match(self, match: "JobMatch") -> dict[str, Any]:
        return {
            "id": match.id,
            "job_id": match.job_id,
            "user_id": match.user_id,
            "score": match.score,
            "category": match.category,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "missing_certifications": match.missing_certifications,
            "missing_technologies": match.missing_technologies,
            "location_compatible": match.location_compatible,
            "experience_compatible": match.experience_compatible,
            "reasoning": match.reasoning,
            "profile_improvements": match.profile_improvements,
            "resume_improvements": match.resume_improvements,
            "created_at": match.created_at,
        }

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "user_id": self.user_id,
            "score": self.score,
            "category": self.category,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "missing_certifications": self.missing_certifications,
            "missing_technologies": self.missing_technologies,
            "location_compatible": self.location_compatible,
            "experience_compatible": self.experience_compatible,
            "reasoning": self.reasoning,
            "profile_improvements": self.profile_improvements,
            "resume_improvements": self.resume_improvements,
            "created_at": self.created_at,
        }


from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobMatch(Base):
    """Persisted job matching analysis for a user and job."""

    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Weak Match", nullable=False)
    matched_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_certifications: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    missing_technologies: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    location_compatible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    experience_compatible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    profile_improvements: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    resume_improvements: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
