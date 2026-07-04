from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.cover_letter_generator import CoverLetter
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User

COVER_LETTER_DIR = Path(__file__).resolve().parents[2] / "uploads" / "cover_letters_generator"
COVER_LETTER_DIR.mkdir(parents=True, exist_ok=True)

VALID_TEMPLATES = {"professional", "modern", "simple"}
VALID_TONES = {"professional", "friendly", "formal", "confident"}
VALID_LENGTHS = {"short", "medium", "long"}

_NOISE_WORDS = {
    "and", "the", "for", "with", "role", "work", "will", "your", "you", "our", "are",
    "that", "this", "from", "have", "has", "been", "into", "using", "use", "able",
    "years", "year", "experience", "required", "preferred", "must", "should",
}

_TECH_PATTERNS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue", "node",
    "fastapi", "django", "flask", "spring", "sql", "postgresql", "mysql", "mongodb",
    "redis", "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "git",
    "linux", "rest", "api", "graphql", "ci/cd", "jenkins", "kafka", "spark",
    "machine learning", "deep learning", "nlp", "data science", "pandas", "numpy",
    "agile", "scrum", "jira", "figma", "c++", "c#", "go", "rust", "ruby", "php",
]


class CoverLetterGeneratorService:
    """Generate cover letters from resume and job description using rule-based logic."""

    def __init__(self, db: Session):
        self.db = db

    def generate(
        self,
        user: User,
        resume_id: int,
        job_description: str,
        job_title: str,
        company_name: str,
        template_name: str = "professional",
        tone: str = "professional",
        length: str = "medium",
    ) -> dict[str, Any]:
        resume = self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
        if resume is None:
            raise ValueError("Resume not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        resume_text = self._extract_resume_text(resume)
        if not resume_text.strip():
            raise ValueError("Resume content is empty or unreadable")

        template = template_name.lower() if template_name.lower() in VALID_TEMPLATES else "professional"
        tone_value = tone.lower() if tone.lower() in VALID_TONES else "professional"
        length_value = length.lower() if length.lower() in VALID_LENGTHS else "medium"

        jd_keywords = self._extract_keywords(job_description)
        matched_skills = self._extract_matched_skills(job_description, resume_text, profile)
        experience_bullets = self._extract_experience_bullets(resume_text)

        generated_letter = self._compose_letter(
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            resume_text=resume_text,
            matched_skills=matched_skills,
            jd_keywords=jd_keywords,
            experience_bullets=experience_bullets,
            template=template,
            tone=tone_value,
            length=length_value,
            profile=profile,
        )

        record = CoverLetter(
            user_id=user.id,
            resume_id=resume.id,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            template_name=template,
            generated_letter=generated_letter,
            tone=tone_value,
            length=length_value,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        files = self._store_files(record, generated_letter)
        record.pdf_path = files["pdf_path"]
        record.docx_path = files["docx_path"]
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return self._to_generate_response(record)

    def history(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(CoverLetter).filter(CoverLetter.user_id == user.id)
        total = query.count()
        items = query.order_by(CoverLetter.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def get_by_id(self, user: User, letter_id: int) -> CoverLetter | None:
        return (
            self.db.query(CoverLetter)
            .filter(CoverLetter.id == letter_id, CoverLetter.user_id == user.id)
            .first()
        )

    def update(self, user: User, letter_id: int, generated_letter: str) -> CoverLetter:
        item = self.get_by_id(user, letter_id)
        if item is None:
            raise ValueError("Cover letter not found")
        item.generated_letter = generated_letter
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        files = self._store_files(item, generated_letter)
        item.pdf_path = files["pdf_path"]
        item.docx_path = files["docx_path"]
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, user: User, letter_id: int) -> None:
        item = self.get_by_id(user, letter_id)
        if item is None:
            raise ValueError("Cover letter not found")
        for maybe_path in [item.pdf_path, item.docx_path]:
            if maybe_path:
                path = Path(maybe_path)
                if path.exists():
                    path.unlink()
        self.db.delete(item)
        self.db.commit()

    def download_pdf(self, user: User, letter_id: int) -> tuple[bytes, str, str]:
        return self._download(user, letter_id, "pdf")

    def download_docx(self, user: User, letter_id: int) -> tuple[bytes, str, str]:
        return self._download(user, letter_id, "docx")

    def _download(self, user: User, letter_id: int, file_format: str) -> tuple[bytes, str, str]:
        item = self.get_by_id(user, letter_id)
        if item is None:
            raise ValueError("Cover letter not found")
        path_map = {
            "pdf": (item.pdf_path, "application/pdf", "pdf"),
            "docx": (item.docx_path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
        }
        if file_format not in path_map:
            raise ValueError("Unsupported file format")
        file_path, content_type, ext = path_map[file_format]
        if not file_path or not Path(file_path).exists():
            raise ValueError(f"{file_format.upper()} output not available")
        label = (item.company_name or "cover_letter").replace(" ", "_").lower()
        return Path(file_path).read_bytes(), content_type, f"cover_letter_{label}_{item.id}.{ext}"

    def count_for_dashboard(self, user: User) -> int:
        return self.db.query(CoverLetter).filter(CoverLetter.user_id == user.id).count()

    def count_this_week_for_dashboard(self, user: User) -> int:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        return (
            self.db.query(CoverLetter)
            .filter(CoverLetter.user_id == user.id, CoverLetter.created_at >= week_ago)
            .count()
        )

    def most_used_template_for_dashboard(self, user: User) -> str | None:
        items = self.db.query(CoverLetter).filter(CoverLetter.user_id == user.id).all()
        if not items:
            return None
        counts = Counter(item.template_name for item in items)
        return counts.most_common(1)[0][0]

    def latest_for_dashboard(self, user: User) -> dict[str, Any] | None:
        item = (
            self.db.query(CoverLetter)
            .filter(CoverLetter.user_id == user.id)
            .order_by(CoverLetter.created_at.desc())
            .first()
        )
        if item is None:
            return None
        return {
            "id": item.id,
            "resume_id": item.resume_id,
            "job_title": item.job_title,
            "company_name": item.company_name,
            "template_name": item.template_name,
            "tone": item.tone,
            "created_at": item.created_at,
        }

    def recent_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        items = (
            self.db.query(CoverLetter)
            .filter(CoverLetter.user_id == user.id)
            .order_by(CoverLetter.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": item.id,
                "resume_id": item.resume_id,
                "job_title": item.job_title,
                "company_name": item.company_name,
                "template_name": item.template_name,
                "tone": item.tone,
                "created_at": item.created_at,
            }
            for item in items
        ]

    def stats_for_dashboard(self, user: User) -> dict[str, Any]:
        return {
            "total_generated": self.count_for_dashboard(user),
            "generated_this_week": self.count_this_week_for_dashboard(user),
            "most_used_template": self.most_used_template_for_dashboard(user),
        }

    def _compose_letter(
        self,
        job_title: str,
        company_name: str,
        job_description: str,
        resume_text: str,
        matched_skills: list[str],
        jd_keywords: list[str],
        experience_bullets: list[str],
        template: str,
        tone: str,
        length: str,
        profile: Profile | None,
    ) -> str:
        intro = self._build_introduction(job_title, company_name, tone, length, resume_text, matched_skills)
        experience_section = self._build_experience_section(experience_bullets, tone, length)
        skills_section = self._build_skills_alignment(matched_skills, jd_keywords, tone, length)
        closing = self._build_closing(company_name, job_title, tone, length)

        if template == "modern":
            sections = [
                f"# Cover Letter — {job_title}",
                f"**{company_name}**",
                "",
                intro,
                "",
                "## Why I'm a Strong Fit",
                experience_section,
                "",
                "## Skills Alignment",
                skills_section,
                "",
                closing,
            ]
        elif template == "simple":
            sections = [intro, "", experience_section, "", skills_section, "", closing]
        else:
            sections = [
                f"Re: Application for {job_title}",
                f"{company_name}",
                "",
                intro,
                "",
                experience_section,
                "",
                skills_section,
                "",
                closing,
            ]

        letter = "\n".join(sections)
        if length == "short":
            return self._truncate_letter(letter, 1200)
        if length == "long":
            extra = self._build_profile_context(profile, resume_text)
            if extra:
                letter += f"\n\n{extra}"
        return letter

    def _build_introduction(
        self, job_title: str, company_name: str, tone: str, length: str, resume_text: str, skills: list[str]
    ) -> str:
        first_line = next((line.strip() for line in resume_text.splitlines() if line.strip()), "")
        skill_phrase = ", ".join(skills[:3]) if skills else "relevant experience"

        tone_openers = {
            "professional": f"I am writing to express my interest in the {job_title} position at {company_name}.",
            "friendly": f"I'm excited to apply for the {job_title} role at {company_name}!",
            "formal": f"I respectfully submit my application for the position of {job_title} at {company_name}.",
            "confident": f"I am confident that my background makes me an excellent candidate for the {job_title} role at {company_name}.",
        }
        opener = tone_openers.get(tone, tone_openers["professional"])

        if length == "short":
            return f"{opener} My experience with {skill_phrase} aligns well with your requirements."

        context = first_line[:200] if first_line else f"I bring hands-on expertise in {skill_phrase}."
        return f"{opener} {context} I am particularly drawn to this opportunity because it aligns with my proven strengths in {skill_phrase}."

    def _build_experience_section(self, bullets: list[str], tone: str, length: str) -> str:
        if not bullets:
            return "Throughout my career, I have consistently delivered results that align with role expectations."

        max_bullets = 2 if length == "short" else 4 if length == "medium" else 6
        selected = bullets[:max_bullets]

        prefix = {
            "professional": "In my professional experience, I have:",
            "friendly": "Here's what I've accomplished:",
            "formal": "My professional accomplishments include:",
            "confident": "My track record demonstrates:",
        }.get(tone, "In my professional experience, I have:")

        lines = [prefix] + [f"- {b}" for b in selected]
        return "\n".join(lines)

    def _build_skills_alignment(self, skills: list[str], keywords: list[str], tone: str, length: str) -> str:
        if not skills:
            return "I am eager to contribute my existing capabilities to your team."

        max_skills = 3 if length == "short" else 5 if length == "medium" else 8
        skill_list = skills[:max_skills]
        keyword_overlap = [kw for kw in keywords if any(kw.lower() in s.lower() for s in skill_list)][:3]

        skill_text = ", ".join(skill_list)
        if keyword_overlap:
            kw_text = ", ".join(keyword_overlap)
            return (
                f"My skills in {skill_text} directly address key requirements mentioned in your posting, "
                f"including {kw_text}."
            )

        closers = {
            "professional": f"My competencies in {skill_text} position me to contribute effectively from day one.",
            "friendly": f"I'd love to bring my skills in {skill_text} to your team!",
            "formal": f"My qualifications encompass {skill_text}, which I understand are central to this role.",
            "confident": f"I have demonstrated proficiency in {skill_text} and am ready to apply these strengths immediately.",
        }
        return closers.get(tone, closers["professional"])

    def _build_closing(self, company_name: str, job_title: str, tone: str, length: str) -> str:
        closings = {
            "professional": f"Thank you for considering my application. I welcome the opportunity to discuss how I can contribute to {company_name} as a {job_title}.",
            "friendly": f"Thanks so much for your time — I'd love to chat more about joining the {company_name} team!",
            "formal": f"I appreciate your consideration and look forward to the possibility of contributing to {company_name} in the capacity of {job_title}.",
            "confident": f"I am eager to bring my expertise to {company_name} and would welcome the chance to discuss the {job_title} role further.",
        }
        closing = closings.get(tone, closings["professional"])
        if length != "short":
            closing += " I am available at your convenience for an interview."
        return closing

    def _build_profile_context(self, profile: Profile | None, resume_text: str) -> str:
        if not profile:
            return ""
        parts: list[str] = []
        if profile.projects:
            project_names = [p.get("name") for p in profile.projects if isinstance(p, dict) and p.get("name")][:2]
            if project_names:
                parts.append(f"Notable projects include {', '.join(project_names)}.")
        if profile.certifications:
            cert_names = [c.get("name") for c in profile.certifications if isinstance(c, dict) and c.get("name")][:2]
            if cert_names:
                parts.append(f"I hold certifications including {', '.join(cert_names)}.")
        return " ".join(parts)

    def _truncate_letter(self, letter: str, max_chars: int) -> str:
        if len(letter) <= max_chars:
            return letter
        return letter[: max_chars - 3].rsplit(" ", 1)[0] + "..."

    def _extract_resume_text(self, resume: Resume) -> str:
        metadata = resume.file_metadata or {}
        content = metadata.get("content")
        if isinstance(content, str) and content.strip():
            return content
        path = Path(resume.storage_path)
        if not path.exists():
            return ""
        return path.read_bytes().decode("utf-8", errors="ignore")

    def _extract_keywords(self, text: str) -> list[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}", text.lower())
        freq: dict[str, int] = {}
        for word in words:
            if word in _NOISE_WORDS or len(word) < 3:
                continue
            freq[word] = freq.get(word, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))
        return [w for w, _ in sorted_words[:25]]

    def _extract_skills_from_text(self, text: str) -> list[str]:
        lower = text.lower()
        found: list[str] = []
        for pattern in _TECH_PATTERNS:
            if pattern in lower:
                found.append(pattern.title() if pattern.isalpha() else pattern.upper())
        return found

    def _extract_matched_skills(self, job_description: str, resume_text: str, profile: Profile | None) -> list[str]:
        jd_skills = set(self._normalize_term(s) for s in self._extract_skills_from_text(job_description))
        resume_skills = set(self._normalize_term(s) for s in self._extract_skills_from_text(resume_text))
        if profile and profile.skills:
            for skill in profile.skills:
                if isinstance(skill, str):
                    resume_skills.add(self._normalize_term(skill))

        matched = jd_skills & resume_skills
        display: list[str] = []
        for skill in self._extract_skills_from_text(job_description):
            if self._normalize_term(skill) in matched:
                display.append(skill)
        if not display and profile and profile.skills:
            display = [s for s in profile.skills if isinstance(s, str)][:5]
        if not display:
            display = self._extract_skills_from_text(resume_text)[:5]
        return display[:10]

    def _extract_experience_bullets(self, resume_text: str) -> list[str]:
        bullets: list[str] = []
        for line in resume_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("-", "•", "*")) or re.match(r"^\d+\.", stripped):
                bullets.append(stripped.lstrip("-•* ").strip())
            elif len(stripped) > 30 and any(
                word in stripped.lower() for word in ("developed", "built", "led", "managed", "implemented", "designed")
            ):
                bullets.append(stripped)
        if not bullets:
            chunks = [c.strip() for c in re.split(r"[\n.;]+", resume_text) if len(c.strip()) > 25]
            bullets = chunks[:5]
        return bullets[:8]

    def _normalize_term(self, term: str) -> str:
        return re.sub(r"[^a-z0-9+#./-]", "", term.lower()).strip()

    def _store_files(self, record: CoverLetter, content: str) -> dict[str, str]:
        prefix = f"user_{record.user_id}_cl_{record.id}"
        pdf_path = COVER_LETTER_DIR / f"{prefix}.pdf"
        docx_path = COVER_LETTER_DIR / f"{prefix}.docx"
        pdf_path.write_bytes(content.encode("utf-8"))
        docx_path.write_bytes(content.encode("utf-8"))
        return {"pdf_path": str(pdf_path), "docx_path": str(docx_path)}

    def _to_generate_response(self, record: CoverLetter) -> dict[str, Any]:
        return {
            "id": record.id,
            "job_title": record.job_title,
            "company_name": record.company_name,
            "template_name": record.template_name,
            "tone": record.tone,
            "length": record.length,
            "generated_letter": record.generated_letter or "",
        }
