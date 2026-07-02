from __future__ import annotations

import hashlib
import html
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.cover_letter import CoverLetterGenerationHistory, CoverLetterTemplate, GeneratedCoverLetter
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import TailoredResume
from app.db.models.user import User
from app.db.session import SessionLocal
from app.services.jobs.match_service import JobMatch

COVER_LETTER_DIR = Path(__file__).resolve().parents[2] / "uploads" / "cover_letters"
COVER_LETTER_DIR.mkdir(parents=True, exist_ok=True)
_GENERATION_EXECUTOR = ThreadPoolExecutor(max_workers=2)
_MAX_RETRIES = 2


class CoverLetterService:
    def __init__(self, db: Session):
        self.db = db

    def generate_for_job(self, user: User, job_id: int) -> dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise ValueError("Job not found")
        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        resume = self._active_resume(user.id)
        if resume is None:
            raise ValueError("Active resume not found")
        tailored = self._latest_tailored_resume(user.id, job.id)
        match = self.db.query(JobMatch).filter(JobMatch.user_id == user.id, JobMatch.job_id == job.id).first()
        template = self._default_template(user)
        signature = self._signature(user.id, job, resume, tailored, profile, match, template)

        cached = (
            self.db.query(GeneratedCoverLetter)
            .filter(
                GeneratedCoverLetter.user_id == user.id,
                GeneratedCoverLetter.job_id == job.id,
                GeneratedCoverLetter.generation_signature == signature,
                GeneratedCoverLetter.status == "completed",
            )
            .order_by(GeneratedCoverLetter.cover_letter_version.desc())
            .first()
        )
        if cached:
            self._create_history(cached, "completed", "Returned cached cover letter", cached.quality_score, retry_count=0)
            return {"cover_letter_id": cached.id, "status": "completed", "cached": True, "message": "Reused matching cover letter."}

        item = GeneratedCoverLetter(
            user_id=user.id,
            job_id=job.id,
            company_name=job.company_name,
            template_id=template.id if template else None,
            resume_id=resume.id,
            tailored_resume_id=tailored.id if tailored else None,
            match_id=match.id if match else None,
            cover_letter_version=self._next_version(user.id, job.id),
            status="queued",
            download_formats=["pdf", "docx", "markdown", "html"],
            generation_signature=signature,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        self._create_history(item, "queued", "Cover letter generation queued", None, retry_count=0)
        _GENERATION_EXECUTOR.submit(self._run_generation_task, item.id, 0)
        return {"cover_letter_id": item.id, "status": "queued", "cached": False, "message": "Cover letter generation started."}

    def get_history(self, user: User, page: int, size: int) -> dict[str, Any]:
        query = self.db.query(CoverLetterGenerationHistory).filter(CoverLetterGenerationHistory.user_id == user.id)
        return {"items": query.order_by(CoverLetterGenerationHistory.created_at.desc()).offset((page - 1) * size).limit(size).all(), "total": query.count(), "page": page, "size": size}

    def get_cover_letter(self, user: User, item_id: int) -> GeneratedCoverLetter | None:
        return self.db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.id == item_id, GeneratedCoverLetter.user_id == user.id).first()

    def delete_cover_letter(self, user: User, item_id: int) -> None:
        item = self.get_cover_letter(user, item_id)
        if item is None:
            raise ValueError("Cover letter not found")
        for maybe_path in [item.markdown_path, item.html_path, item.pdf_path, item.docx_path]:
            if maybe_path and Path(maybe_path).exists():
                Path(maybe_path).unlink()
        self.db.query(CoverLetterGenerationHistory).filter(CoverLetterGenerationHistory.generated_cover_letter_id == item.id).delete()
        self.db.delete(item)
        self.db.commit()

    def download(self, user: User, item_id: int, file_format: str = "pdf") -> tuple[bytes, str, str]:
        item = self.get_cover_letter(user, item_id)
        if item is None:
            raise ValueError("Cover letter not found")
        if item.status != "completed":
            raise ValueError("Cover letter generation is not complete yet")
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
        return Path(file_path).read_bytes(), content_type, f"cover_letter_job_{item.job_id}_v{item.cover_letter_version}.{ext}"

    def list_templates(self, user: User) -> list[CoverLetterTemplate]:
        return self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.user_id == user.id).order_by(CoverLetterTemplate.updated_at.desc()).all()

    def create_template(self, user: User, payload: dict[str, Any]) -> CoverLetterTemplate:
        version = ((self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.user_id == user.id).order_by(CoverLetterTemplate.version.desc()).first() or CoverLetterTemplate(version=0)).version + 1)
        item = CoverLetterTemplate(user_id=user.id, version=version, **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_template(self, user: User, template_id: int, payload: dict[str, Any]) -> CoverLetterTemplate:
        item = self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.id == template_id, CoverLetterTemplate.user_id == user.id).first()
        if item is None:
            raise ValueError("Template not found")
        for key, value in payload.items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_template(self, user: User, template_id: int) -> None:
        item = self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.id == template_id, CoverLetterTemplate.user_id == user.id).first()
        if item is None:
            raise ValueError("Template not found")
        self.db.delete(item)
        self.db.commit()

    def recent_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        rows = self.db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.user_id == user.id, GeneratedCoverLetter.status == "completed").order_by(GeneratedCoverLetter.generated_at.desc(), GeneratedCoverLetter.created_at.desc()).limit(limit).all()
        return [{"id": row.id, "job_id": row.job_id, "company_name": row.company_name, "cover_letter_version": row.cover_letter_version, "quality_score": row.quality_score, "generated_at": row.generated_at, "status": row.status} for row in rows]

    def history_for_dashboard(self, user: User, limit: int = 8) -> list[dict[str, Any]]:
        rows = self.db.query(CoverLetterGenerationHistory).filter(CoverLetterGenerationHistory.user_id == user.id).order_by(CoverLetterGenerationHistory.created_at.desc()).limit(limit).all()
        return [{"id": row.id, "generated_cover_letter_id": row.generated_cover_letter_id, "job_id": row.job_id, "company_name": row.company_name, "status": row.status, "message": row.message, "quality_score": row.quality_score, "created_at": row.created_at} for row in rows]

    def template_usage_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        rows = self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.user_id == user.id).order_by(CoverLetterTemplate.updated_at.desc()).limit(limit).all()
        return [{"id": row.id, "name": row.name, "is_default": row.is_default, "version": row.version, "updated_at": row.updated_at} for row in rows]

    def stats_for_dashboard(self, user: User) -> dict[str, Any]:
        items = self.db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.user_id == user.id).all()
        completed = [item for item in items if item.status == "completed"]
        cache_hits = self.db.query(CoverLetterGenerationHistory).filter(CoverLetterGenerationHistory.user_id == user.id, CoverLetterGenerationHistory.message == "Returned cached cover letter").count()
        return {"total_generated": len(completed), "queued_or_processing": sum(1 for i in items if i.status in {"queued", "processing"}), "failed": sum(1 for i in items if i.status == "failed"), "average_quality_score": round(sum(float(i.quality_score or 0) for i in completed) / len(completed), 1) if completed else None, "cache_hits": cache_hits}

    def _run_generation_task(self, cover_letter_id: int, retry_count: int) -> None:
        db = SessionLocal()
        try:
            item = db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.id == cover_letter_id).first()
            if item is None:
                return
            item.status = "processing"
            db.add(item)
            db.commit()
            self._create_history(item, "processing", "Analyzing job and profile context", None, retry_count=retry_count, db=db)

            job = db.query(Job).filter(Job.id == item.job_id).first()
            user = db.query(User).filter(User.id == item.user_id).first()
            profile = db.query(Profile).filter(Profile.user_id == item.user_id).first()
            resume = db.query(Resume).filter(Resume.id == item.resume_id).first() if item.resume_id else None
            tailored = db.query(TailoredResume).filter(TailoredResume.id == item.tailored_resume_id).first() if item.tailored_resume_id else None
            match = db.query(JobMatch).filter(JobMatch.id == item.match_id).first() if item.match_id else None
            template = db.query(CoverLetterTemplate).filter(CoverLetterTemplate.id == item.template_id).first() if item.template_id else None
            if job is None or resume is None:
                raise ValueError("Missing job/resume context")

            analysis = self._analyze(job)
            sections = self._build_sections(job, user, profile, tailored, match, template)
            markdown = self._build_markdown(job, analysis, sections)
            html_output = self._build_html(markdown)
            quality_score = self._quality_score(analysis, markdown)
            files = self._store_files(item, markdown, html_output)

            item.analysis = analysis
            item.sections = sections
            item.markdown_content = markdown
            item.html_content = html_output
            item.markdown_path = files["markdown_path"]
            item.html_path = files["html_path"]
            item.pdf_path = files["pdf_path"]
            item.docx_path = files["docx_path"]
            item.status = "completed"
            item.quality_score = quality_score
            item.generated_at = datetime.utcnow()
            db.add(item)
            db.commit()
            self._create_history(item, "completed", "Cover letter generated", quality_score, retry_count=retry_count, db=db)
        except Exception as exc:  # noqa: BLE001
            failed = db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.id == cover_letter_id).first()
            if failed:
                failed.status = "failed"
                db.add(failed)
                db.commit()
                self._create_history(failed, "failed", f"Generation failed: {exc}", None, retry_count=retry_count, db=db)
                if retry_count < _MAX_RETRIES:
                    self._create_history(failed, "queued", "Retry queued after failure", None, retry_count=retry_count + 1, db=db)
                    _GENERATION_EXECUTOR.submit(self._run_generation_task, failed.id, retry_count + 1)
        finally:
            db.close()

    def _active_resume(self, user_id: int) -> Resume | None:
        return self.db.query(Resume).filter(Resume.user_id == user_id, Resume.is_active.is_(True)).order_by(Resume.version.desc()).first()

    def _latest_tailored_resume(self, user_id: int, job_id: int) -> TailoredResume | None:
        return self.db.query(TailoredResume).filter(TailoredResume.user_id == user_id, TailoredResume.job_id == job_id, TailoredResume.status == "completed").order_by(TailoredResume.resume_version.desc()).first()

    def _default_template(self, user: User) -> CoverLetterTemplate | None:
        return self.db.query(CoverLetterTemplate).filter(CoverLetterTemplate.user_id == user.id, CoverLetterTemplate.is_default.is_(True)).order_by(CoverLetterTemplate.updated_at.desc()).first()

    def _next_version(self, user_id: int, job_id: int) -> int:
        item = self.db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.user_id == user_id, GeneratedCoverLetter.job_id == job_id).order_by(GeneratedCoverLetter.cover_letter_version.desc()).first()
        return (item.cover_letter_version if item else 0) + 1

    def _signature(self, user_id: int, job: Job, resume: Resume, tailored: TailoredResume | None, profile: Profile | None, match: JobMatch | None, template: CoverLetterTemplate | None) -> str:
        payload = "|".join([str(user_id), str(job.id), str(job.updated_at or ""), str(resume.id), str(resume.updated_at or ""), str(tailored.updated_at if tailored else ""), str(profile.updated_at if profile else ""), str(match.created_at if match else ""), str(template.updated_at if template else "")])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _analyze(self, job: Job) -> dict[str, Any]:
        description = job.description or ""
        keywords = self._extract_keywords(description)
        return {
            "company_name": job.company_name or "",
            "role": job.title or "",
            "responsibilities": self._split_points(description)[:8],
            "required_skills": (job.skills or [])[:10],
            "preferred_skills": (job.tags or [])[:8],
            "company_values": [point for point in self._split_points(description) if any(token in point.lower() for token in ["value", "mission", "culture", "collaborative", "ownership"])][:5],
            "industry": self._guess_industry(description),
            "keywords": keywords[:20],
        }

    def _build_sections(
        self,
        job: Job,
        user: User | None,
        profile: Profile | None,
        tailored: TailoredResume | None,
        match: JobMatch | None,
        template: CoverLetterTemplate | None,
    ) -> dict[str, Any]:
        full_name = user.full_name if user and user.full_name else "Candidate"
        skills = profile.skills if profile and profile.skills else []
        projects = [p.get("name") for p in (profile.projects if profile else []) if isinstance(p, dict) and p.get("name")]
        certs = [c.get("name") for c in (profile.certifications if profile else []) if isinstance(c, dict) and c.get("name")]
        intro = f"Dear Hiring Manager,\n\nI am excited to apply for the {job.title} role at {job.company_name}. "
        if template and template.intro_style:
            intro += f"My approach aligns with a {template.intro_style.lower()} communication style and clear business impact."
        interest = match.reasoning if match and match.reasoning else f"I am drawn to this opportunity because it blends {', '.join((job.skills or [])[:3])} with high-impact delivery."
        closing = "Thank you for considering my application. I would welcome the opportunity to discuss how my background can support your team goals."
        if template and template.closing_style:
            closing = f"{closing} I aim to keep communication {template.closing_style.lower()} and outcomes-focused."
        signature = template.signature_block if template and template.signature_block else full_name
        if tailored and tailored.markdown_content:
            projects = projects + [line.strip("- ").strip() for line in tailored.markdown_content.splitlines() if line.startswith("- ")][:2]
        return {
            "introduction": intro,
            "role_interest": interest,
            "relevant_skills": skills[:8] or (job.skills or [])[:8],
            "relevant_projects": list(dict.fromkeys(projects))[:4],
            "certifications": certs[:4],
            "closing_paragraph": closing,
            "professional_signature": signature,
        }

    def _build_markdown(self, job: Job, analysis: dict[str, Any], sections: dict[str, Any]) -> str:
        return "\n".join(
            [
                f"# Cover Letter - {job.title}",
                "",
                sections.get("introduction", ""),
                "",
                "## Why this role",
                sections.get("role_interest", ""),
                "",
                "## Relevant skills",
                *(f"- {skill}" for skill in sections.get("relevant_skills", [])),
                "",
                "## Relevant projects",
                *(f"- {project}" for project in sections.get("relevant_projects", [])),
                "",
                "## Certifications",
                *(f"- {cert}" for cert in sections.get("certifications", [])),
                "",
                "## Alignment keywords",
                *(f"- {kw}" for kw in analysis.get("keywords", [])),
                "",
                sections.get("closing_paragraph", ""),
                "",
                f"Sincerely,\n{sections.get('professional_signature', '')}",
            ]
        )

    def _build_html(self, markdown_text: str) -> str:
        escaped = html.escape(markdown_text)
        return "<html><head><meta charset='utf-8'><title>Cover Letter</title></head><body style='font-family: Arial, sans-serif; margin: 32px; line-height: 1.6;'><pre style='white-space: pre-wrap;'>" + escaped + "</pre></body></html>"

    def _store_files(self, item: GeneratedCoverLetter, markdown_text: str, html_text: str) -> dict[str, str]:
        prefix = f"user_{item.user_id}_job_{item.job_id}_cover_letter_v{item.cover_letter_version}"
        md_path = COVER_LETTER_DIR / f"{prefix}.md"
        html_path = COVER_LETTER_DIR / f"{prefix}.html"
        pdf_path = COVER_LETTER_DIR / f"{prefix}.pdf"
        docx_path = COVER_LETTER_DIR / f"{prefix}.docx"
        md_path.write_text(markdown_text, encoding="utf-8")
        html_path.write_text(html_text, encoding="utf-8")
        pdf_path.write_bytes(markdown_text.encode("utf-8"))
        docx_path.write_bytes(markdown_text.encode("utf-8"))
        return {"markdown_path": str(md_path), "html_path": str(html_path), "pdf_path": str(pdf_path), "docx_path": str(docx_path)}

    def _quality_score(self, analysis: dict[str, Any], markdown_text: str) -> float:
        keywords = [kw.lower() for kw in analysis.get("keywords", []) if isinstance(kw, str)]
        if not keywords:
            return 80.0
        lowered = markdown_text.lower()
        hits = sum(1 for kw in keywords if kw and kw in lowered)
        return round(min(98.0, 60.0 + (hits / max(1, len(keywords))) * 38.0), 1)

    def _extract_keywords(self, text: str) -> list[str]:
        words = [w.strip() for w in re.split(r"[^A-Za-z0-9+#.]+", text) if w.strip()]
        noise = {"and", "the", "for", "with", "role", "work", "will", "your", "you", "our", "are"}
        result: list[str] = []
        for word in words:
            if len(word) < 3 or word.lower() in noise:
                continue
            if word not in result:
                result.append(word)
        return result

    def _split_points(self, text: str) -> list[str]:
        return [chunk.strip() for chunk in re.split(r"[\n.;]+", text or "") if chunk.strip()]

    def _guess_industry(self, description: str) -> str | None:
        lowered = (description or "").lower()
        if any(token in lowered for token in ["health", "medical", "clinical"]):
            return "Healthcare"
        if any(token in lowered for token in ["fintech", "bank", "payment"]):
            return "Finance"
        if any(token in lowered for token in ["saas", "software", "platform"]):
            return "Technology"
        return None

    def _create_history(self, item: GeneratedCoverLetter, status: str, message: str, quality_score: float | None, retry_count: int, db: Session | None = None) -> None:
        target_db = db or self.db
        target_db.add(
            CoverLetterGenerationHistory(
                generated_cover_letter_id=item.id,
                user_id=item.user_id,
                job_id=item.job_id,
                company_name=item.company_name,
                status=status,
                message=message,
                retry_count=retry_count,
                quality_score=quality_score,
                generated_at=item.generated_at,
            )
        )
        target_db.commit()
