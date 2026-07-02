from __future__ import annotations

import hashlib
import html
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import ResumeGenerationHistory, ResumeTemplate, TailoredResume
from app.db.models.user import User
from app.db.session import SessionLocal
from app.services.jobs.match_service import JobMatch

TAILORED_RESUME_DIR = Path(__file__).resolve().parents[2] / "uploads" / "tailored_resumes"
TAILORED_RESUME_DIR.mkdir(parents=True, exist_ok=True)

_GENERATION_EXECUTOR = ThreadPoolExecutor(max_workers=2)


class ResumeTailoringService:
    def __init__(self, db: Session):
        self.db = db

    def generate_for_job(self, user: User, job_id: int) -> dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise ValueError("Job not found")

        resume = (
            self.db.query(Resume)
            .filter(Resume.user_id == user.id, Resume.is_active.is_(True))
            .order_by(Resume.version.desc())
            .first()
        )
        if resume is None:
            raise ValueError("Active resume not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        match = self.db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id).first()

        signature = self._build_generation_signature(user.id, job, resume, profile, match)
        cached = (
            self.db.query(TailoredResume)
            .filter(
                TailoredResume.user_id == user.id,
                TailoredResume.job_id == job.id,
                TailoredResume.generation_signature == signature,
                TailoredResume.status == "completed",
            )
            .order_by(TailoredResume.resume_version.desc())
            .first()
        )
        if cached:
            self._create_history(cached, "completed", "Returned cached tailored resume", cached.ats_score)
            return {
                "tailored_resume_id": cached.id,
                "status": cached.status,
                "cached": True,
                "message": "A matching tailored resume already exists and was reused.",
            }

        version = self._next_version(user.id, job.id)
        template = self._create_template(user, resume, profile)
        tailored = TailoredResume(
            user_id=user.id,
            job_id=job.id,
            template_id=template.id,
            match_id=match.id if match else None,
            resume_version=version,
            status="queued",
            generation_signature=signature,
        )
        self.db.add(tailored)
        self.db.commit()
        self.db.refresh(tailored)
        self._create_history(tailored, "queued", "Resume generation queued", None)

        _GENERATION_EXECUTOR.submit(self._run_generation_task, tailored.id)
        return {
            "tailored_resume_id": tailored.id,
            "status": "queued",
            "cached": False,
            "message": "Resume generation started.",
        }

    def get_history(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(ResumeGenerationHistory).filter(ResumeGenerationHistory.user_id == user.id)
        total = query.count()
        items = query.order_by(ResumeGenerationHistory.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def get_tailored_resume(self, user: User, tailored_id: int) -> TailoredResume | None:
        return self.db.query(TailoredResume).filter(TailoredResume.id == tailored_id, TailoredResume.user_id == user.id).first()

    def delete_tailored_resume(self, user: User, tailored_id: int) -> None:
        item = self.get_tailored_resume(user, tailored_id)
        if item is None:
            raise ValueError("Tailored resume not found")
        for maybe_path in [item.markdown_path, item.html_path, item.pdf_path, item.docx_path]:
            if maybe_path:
                path = Path(maybe_path)
                if path.exists():
                    path.unlink()
        self.db.query(ResumeGenerationHistory).filter(ResumeGenerationHistory.tailored_resume_id == item.id).delete()
        self.db.delete(item)
        self.db.commit()

    def download(self, user: User, tailored_id: int, file_format: str = "pdf") -> tuple[bytes, str, str]:
        item = self.get_tailored_resume(user, tailored_id)
        if item is None:
            raise ValueError("Tailored resume not found")
        if item.status != "completed":
            raise ValueError("Resume generation is not complete yet")

        format_value = (file_format or "pdf").lower()
        path_map = {
            "pdf": (item.pdf_path, "application/pdf", "pdf"),
            "docx": (item.docx_path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
            "markdown": (item.markdown_path, "text/markdown; charset=utf-8", "md"),
            "html": (item.html_path, "text/html; charset=utf-8", "html"),
        }
        if format_value not in path_map:
            raise ValueError("Unsupported file format")
        file_path, content_type, ext = path_map[format_value]
        if not file_path or not Path(file_path).exists():
            raise ValueError(f"{format_value.upper()} output not available")
        return Path(file_path).read_bytes(), content_type, f"tailored_resume_job_{item.job_id}_v{item.resume_version}.{ext}"

    def recent_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        items = (
            self.db.query(TailoredResume)
            .filter(TailoredResume.user_id == user.id, TailoredResume.status == "completed")
            .order_by(TailoredResume.generated_at.desc(), TailoredResume.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": item.id,
                "job_id": item.job_id,
                "resume_version": item.resume_version,
                "ats_score": item.ats_score,
                "generated_at": item.generated_at,
                "status": item.status,
            }
            for item in items
        ]

    def history_for_dashboard(self, user: User, limit: int = 8) -> list[dict[str, Any]]:
        rows = (
            self.db.query(ResumeGenerationHistory)
            .filter(ResumeGenerationHistory.user_id == user.id)
            .order_by(ResumeGenerationHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": row.id,
                "tailored_resume_id": row.tailored_resume_id,
                "job_id": row.job_id,
                "status": row.status,
                "message": row.message,
                "ats_score": row.ats_score,
                "generated_at": row.generated_at,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    def suggestions_for_dashboard(self, user: User, limit: int = 6) -> list[str]:
        latest = (
            self.db.query(TailoredResume)
            .filter(TailoredResume.user_id == user.id, TailoredResume.status == "completed")
            .order_by(TailoredResume.generated_at.desc(), TailoredResume.created_at.desc())
            .first()
        )
        if not latest or not isinstance(latest.improvements, dict):
            return []
        suggestions: list[str] = []
        for key in ("keyword_optimization", "ats_optimization", "achievements"):
            value = latest.improvements.get(key, [])
            if isinstance(value, list):
                suggestions.extend([str(item) for item in value if item])
        return suggestions[:limit]

    def ats_average_for_dashboard(self, user: User) -> float | None:
        items = (
            self.db.query(TailoredResume)
            .filter(TailoredResume.user_id == user.id, TailoredResume.status == "completed", TailoredResume.ats_score.isnot(None))
            .all()
        )
        if not items:
            return None
        return round(sum(float(item.ats_score or 0) for item in items) / len(items), 1)

    def _run_generation_task(self, tailored_id: int) -> None:
        db = SessionLocal()
        try:
            item = db.query(TailoredResume).filter(TailoredResume.id == tailored_id).first()
            if item is None:
                return
            item.status = "processing"
            db.add(item)
            db.commit()
            self._create_history(item, "processing", "Extracting job and resume context", None, db=db)

            job = db.query(Job).filter(Job.id == item.job_id).first()
            template = db.query(ResumeTemplate).filter(ResumeTemplate.id == item.template_id).first()
            profile = db.query(Profile).filter(Profile.user_id == item.user_id).first()
            match = db.query(JobMatch).filter(JobMatch.id == item.match_id).first() if item.match_id else None
            if job is None or template is None:
                item.status = "failed"
                db.add(item)
                db.commit()
                self._create_history(item, "failed", "Missing template or job context", None, db=db)
                return

            analysis = self._analyze(job)
            improvements = self._build_improvements(analysis, profile, match)
            markdown = self._build_markdown(job, template, analysis, improvements)
            html_output = self._build_html(markdown)
            ats_score = self._compute_ats_score(analysis, markdown)
            files = self._store_generated_files(item, markdown, html_output)

            item.analysis = analysis
            item.improvements = improvements
            item.markdown_content = markdown
            item.html_content = html_output
            item.markdown_path = files["markdown_path"]
            item.html_path = files["html_path"]
            item.pdf_path = files["pdf_path"]
            item.docx_path = files["docx_path"]
            item.ats_score = ats_score
            item.status = "completed"
            item.generated_at = datetime.utcnow()
            db.add(item)
            db.commit()
            self._create_history(item, "completed", "Tailored resume generated", ats_score, db=db)
        except Exception as exc:  # noqa: BLE001
            failed = db.query(TailoredResume).filter(TailoredResume.id == tailored_id).first()
            if failed:
                failed.status = "failed"
                db.add(failed)
                db.commit()
                self._create_history(failed, "failed", f"Generation failed: {exc}", None, db=db)
        finally:
            db.close()

    def _next_version(self, user_id: int, job_id: int) -> int:
        latest = (
            self.db.query(TailoredResume)
            .filter(TailoredResume.user_id == user_id, TailoredResume.job_id == job_id)
            .order_by(TailoredResume.resume_version.desc())
            .first()
        )
        return (latest.resume_version if latest else 0) + 1

    def _create_template(self, user: User, resume: Resume, profile: Profile | None) -> ResumeTemplate:
        source_content = self._extract_resume_text(resume)
        version = (
            (self.db.query(ResumeTemplate).filter(ResumeTemplate.user_id == user.id).order_by(ResumeTemplate.version.desc()).first() or ResumeTemplate(version=0)).version
            + 1
        )
        template = ResumeTemplate(
            user_id=user.id,
            resume_id=resume.id,
            profile_id=profile.id if profile else None,
            version=version,
            source_filename=resume.filename,
            source_content_type=resume.content_type,
            source_storage_path=resume.storage_path,
            source_resume_content=source_content,
            snapshot_data={
                "profile": {
                    "skills": profile.skills if profile else [],
                    "education": profile.education if profile else [],
                    "certifications": profile.certifications if profile else [],
                    "projects": profile.projects if profile else [],
                },
                "resume_metadata": resume.file_metadata or {},
            },
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def _extract_resume_text(self, resume: Resume) -> str:
        metadata = resume.file_metadata or {}
        content = metadata.get("content")
        if isinstance(content, str) and content.strip():
            return content
        path = Path(resume.storage_path)
        if not path.exists():
            return ""
        raw = path.read_bytes()
        return raw.decode("utf-8", errors="ignore")

    def _build_generation_signature(self, user_id: int, job: Job, resume: Resume, profile: Profile | None, match: JobMatch | None) -> str:
        payload = "|".join(
            [
                str(user_id),
                str(job.id),
                str(job.updated_at or ""),
                str(resume.id),
                str(resume.updated_at or ""),
                str(profile.updated_at if profile else ""),
                str(match.created_at if match else ""),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _analyze(self, job: Job) -> dict[str, Any]:
        description = job.description or ""
        keywords = self._extract_keywords(description)
        responsibilities = self._split_points(description)
        return {
            "required_skills": job.skills or keywords[:8],
            "preferred_skills": (job.tags or [])[:8],
            "technologies": list(dict.fromkeys((job.skills or []) + (job.tags or []) + keywords[:12]))[:12],
            "experience": job.experience,
            "keywords": keywords[:20],
            "responsibilities": responsibilities[:8],
            "education": job.education or [],
            "certifications": [tag for tag in (job.tags or []) if "cert" in str(tag).lower()][:6],
        }

    def _build_improvements(self, analysis: dict[str, Any], profile: Profile | None, match: JobMatch | None) -> dict[str, Any]:
        skills = analysis.get("required_skills", [])[:10]
        profile_projects = [p.get("name") for p in (profile.projects or []) if isinstance(p, dict) and p.get("name")] if profile else []
        profile_certs = [c.get("name") for c in (profile.certifications or []) if isinstance(c, dict) and c.get("name")] if profile else []
        summary = "Results-driven professional tailored for this role with focus on impact, ownership, and ATS-relevant outcomes."
        if match and match.reasoning:
            summary = match.reasoning
        return {
            "professional_summary": summary,
            "skills_ordering": skills,
            "relevant_projects": profile_projects[:4],
            "relevant_certifications": profile_certs[:4],
            "achievements": [
                "Delivered measurable project outcomes aligned to role expectations.",
                "Improved reliability and maintainability through production-grade practices.",
            ],
            "keyword_optimization": [f"Include keyword '{kw}' naturally in experience bullets." for kw in analysis.get("keywords", [])[:6]],
            "ats_optimization": [
                "Use role-aligned section headings and concise bullet points.",
                "Mirror job-title terminology where experience supports it.",
                "Prioritize role-critical skills near the top of the resume.",
            ],
        }

    def _build_markdown(self, job: Job, template: ResumeTemplate, analysis: dict[str, Any], improvements: dict[str, Any]) -> str:
        projects = improvements.get("relevant_projects", [])
        certs = improvements.get("relevant_certifications", [])
        skills = improvements.get("skills_ordering", [])
        responsibilities = analysis.get("responsibilities", [])
        return "\n".join(
            [
                f"# Tailored Resume for {job.title}",
                "",
                "## Professional Summary",
                improvements.get("professional_summary", ""),
                "",
                "## Core Skills",
                *(f"- {skill}" for skill in skills),
                "",
                "## Relevant Experience Highlights",
                *(f"- {point}" for point in responsibilities),
                "",
                "## Relevant Projects",
                *(f"- {project}" for project in projects),
                "",
                "## Certifications",
                *(f"- {cert}" for cert in certs),
                "",
                "## ATS Optimization Notes",
                *(f"- {note}" for note in improvements.get("ats_optimization", [])),
                "",
                "## Keyword Optimization",
                *(f"- {note}" for note in improvements.get("keyword_optimization", [])),
                "",
                "## Source Resume Snapshot",
                f"- Filename: {template.source_filename or 'N/A'}",
                f"- Resume Template Version: {template.version}",
            ]
        )

    def _build_html(self, markdown_text: str) -> str:
        escaped = html.escape(markdown_text)
        return (
            "<html><head><meta charset='utf-8'><title>Tailored Resume</title></head>"
            "<body style='font-family: Arial, sans-serif; margin: 32px; line-height: 1.5;'>"
            f"<pre style='white-space: pre-wrap;'>{escaped}</pre>"
            "</body></html>"
        )

    def _store_generated_files(self, item: TailoredResume, markdown_text: str, html_text: str) -> dict[str, str]:
        prefix = f"user_{item.user_id}_job_{item.job_id}_v{item.resume_version}"
        md_path = TAILORED_RESUME_DIR / f"{prefix}.md"
        html_path = TAILORED_RESUME_DIR / f"{prefix}.html"
        pdf_path = TAILORED_RESUME_DIR / f"{prefix}.pdf"
        docx_path = TAILORED_RESUME_DIR / f"{prefix}.docx"
        md_path.write_text(markdown_text, encoding="utf-8")
        html_path.write_text(html_text, encoding="utf-8")
        # Lightweight text-backed placeholders keep format outputs available without extra system dependencies.
        pdf_path.write_bytes(markdown_text.encode("utf-8"))
        docx_path.write_bytes(markdown_text.encode("utf-8"))
        return {
            "markdown_path": str(md_path),
            "html_path": str(html_path),
            "pdf_path": str(pdf_path),
            "docx_path": str(docx_path),
        }

    def _compute_ats_score(self, analysis: dict[str, Any], markdown_text: str) -> float:
        keywords = [kw.lower() for kw in analysis.get("keywords", []) if isinstance(kw, str)]
        if not keywords:
            return 75.0
        content = markdown_text.lower()
        matched = sum(1 for kw in keywords if kw and kw in content)
        score = min(98.0, 55.0 + (matched / max(1, len(keywords))) * 45.0)
        return round(score, 1)

    def _extract_keywords(self, text: str) -> list[str]:
        words = [w.strip() for w in re.split(r"[^A-Za-z0-9+#.]+", text) if w.strip()]
        noise = {"and", "the", "for", "with", "role", "work", "will", "your", "you", "our", "are"}
        result: list[str] = []
        for word in words:
            if len(word) < 3:
                continue
            if word.lower() in noise:
                continue
            if word not in result:
                result.append(word)
        return result

    def _split_points(self, text: str) -> list[str]:
        chunks = [chunk.strip() for chunk in re.split(r"[\n.;]+", text or "") if chunk.strip()]
        return chunks

    def _create_history(
        self,
        item: TailoredResume,
        status: str,
        message: str,
        ats_score: float | None,
        db: Session | None = None,
    ) -> None:
        target_db = db or self.db
        history = ResumeGenerationHistory(
            tailored_resume_id=item.id,
            user_id=item.user_id,
            job_id=item.job_id,
            status=status,
            message=message,
            ats_score=ats_score,
            generated_at=item.generated_at,
        )
        target_db.add(history)
        target_db.commit()
