from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.resume_optimization import ResumeOptimization
from app.db.models.user import User

OPTIMIZED_RESUME_DIR = Path(__file__).resolve().parents[2] / "uploads" / "optimized_resumes"
OPTIMIZED_RESUME_DIR.mkdir(parents=True, exist_ok=True)

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
    "scikit-learn", "tensorflow", "pytorch", "html", "css", "sass", "tailwind",
    "agile", "scrum", "jira", "figma", "c++", "c#", "go", "rust", "ruby", "php",
    "swift", "kotlin", "scala", "hadoop", "hive", "airflow", "elasticsearch",
]


class ResumeOptimizerService:
    """Analyze resume against a job description and produce ATS-optimized output."""

    def __init__(self, db: Session):
        self.db = db

    def analyze(self, user: User, resume_id: int, job_description: str, job_title: str | None = None, company_name: str | None = None) -> dict[str, Any]:
        resume = self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
        if resume is None:
            raise ValueError("Resume not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        resume_text = self._extract_resume_text(resume)
        if not resume_text.strip():
            raise ValueError("Resume content is empty or unreadable")

        jd_analysis = self._parse_job_description(job_description)
        user_inventory = self._build_user_inventory(resume, profile, resume_text)

        matched_keywords, missing_keywords = self._compare_keywords(jd_analysis["keywords"], resume_text, user_inventory)
        matched_skills, missing_skills = self._compare_skills(jd_analysis["skills"], user_inventory)

        keyword_match = self._percentage_score(len(matched_keywords), len(jd_analysis["keywords"]))
        skill_match = self._percentage_score(len(matched_skills), len(jd_analysis["skills"]))
        experience_match = self._experience_score(jd_analysis.get("experience_requirement"), user_inventory)
        education_match = self._education_score(jd_analysis.get("education_requirements", []), user_inventory)

        ats_score = self._compute_ats_score(keyword_match, skill_match, resume_text, jd_analysis["keywords"])
        overall_score = round(
            (ats_score * 0.3 + keyword_match * 0.25 + skill_match * 0.25 + experience_match * 0.1 + education_match * 0.1),
            1,
        )

        recommendations = self._build_recommendations(
            matched_keywords, missing_keywords, matched_skills, missing_skills, keyword_match, skill_match
        )
        recommended_keywords = [kw for kw in missing_keywords if kw in jd_analysis["keywords"]][:8]
        tailored_resume = self._generate_tailored_resume(
            resume_text=resume_text,
            user_inventory=user_inventory,
            jd_analysis=jd_analysis,
            matched_skills=matched_skills,
            missing_keywords=recommended_keywords,
            job_title=job_title or jd_analysis.get("job_title"),
            company_name=company_name or jd_analysis.get("company_name"),
        )

        parsed_title = job_title or jd_analysis.get("job_title")
        parsed_company = company_name or jd_analysis.get("company_name")
        score_breakdown = {
            "ats_score": ats_score,
            "keyword_match": keyword_match,
            "skill_match": skill_match,
            "experience_match": experience_match,
            "education_match": education_match,
            "overall_score": overall_score,
        }

        record = ResumeOptimization(
            user_id=user.id,
            resume_id=resume.id,
            job_title=parsed_title,
            company_name=parsed_company,
            ats_score=ats_score,
            overall_score=overall_score,
            score_breakdown=score_breakdown,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            recommendations=recommendations,
            tailored_resume=tailored_resume,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        files = self._store_output_files(record, tailored_resume)
        record.pdf_path = files["pdf_path"]
        record.docx_path = files["docx_path"]
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return self._to_analyze_response(record)

    def get_history(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(ResumeOptimization).filter(ResumeOptimization.user_id == user.id)
        total = query.count()
        items = query.order_by(ResumeOptimization.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def get_analysis(self, user: User, analysis_id: int) -> ResumeOptimization | None:
        return (
            self.db.query(ResumeOptimization)
            .filter(ResumeOptimization.id == analysis_id, ResumeOptimization.user_id == user.id)
            .first()
        )

    def delete_analysis(self, user: User, analysis_id: int) -> None:
        item = self.get_analysis(user, analysis_id)
        if item is None:
            raise ValueError("Analysis not found")
        for maybe_path in [item.pdf_path, item.docx_path]:
            if maybe_path:
                path = Path(maybe_path)
                if path.exists():
                    path.unlink()
        self.db.delete(item)
        self.db.commit()

    def download(self, user: User, analysis_id: int, file_format: str = "pdf") -> tuple[bytes, str, str]:
        item = self.get_analysis(user, analysis_id)
        if item is None:
            raise ValueError("Analysis not found")
        format_value = (file_format or "pdf").lower()
        path_map = {
            "pdf": (item.pdf_path, "application/pdf", "pdf"),
            "docx": (item.docx_path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx"),
        }
        if format_value not in path_map:
            raise ValueError("Unsupported file format")
        file_path, content_type, ext = path_map[format_value]
        if not file_path or not Path(file_path).exists():
            raise ValueError(f"{format_value.upper()} output not available")
        label = (item.job_title or "resume").replace(" ", "_").lower()
        return Path(file_path).read_bytes(), content_type, f"optimized_{label}_{item.id}.{ext}"

    def count_for_dashboard(self, user: User) -> int:
        return self.db.query(ResumeOptimization).filter(ResumeOptimization.user_id == user.id).count()

    def average_ats_for_dashboard(self, user: User) -> float | None:
        items = self.db.query(ResumeOptimization).filter(ResumeOptimization.user_id == user.id).all()
        if not items:
            return None
        return round(sum(float(item.ats_score) for item in items) / len(items), 1)

    def highest_ats_for_dashboard(self, user: User) -> float | None:
        items = self.db.query(ResumeOptimization).filter(ResumeOptimization.user_id == user.id).all()
        if not items:
            return None
        return max(float(item.ats_score) for item in items)

    def latest_for_dashboard(self, user: User) -> dict[str, Any] | None:
        item = (
            self.db.query(ResumeOptimization)
            .filter(ResumeOptimization.user_id == user.id)
            .order_by(ResumeOptimization.created_at.desc())
            .first()
        )
        if item is None:
            return None
        return {
            "id": item.id,
            "resume_id": item.resume_id,
            "job_title": item.job_title,
            "company_name": item.company_name,
            "ats_score": item.ats_score,
            "overall_score": item.overall_score,
            "created_at": item.created_at,
        }

    def recent_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        items = (
            self.db.query(ResumeOptimization)
            .filter(ResumeOptimization.user_id == user.id)
            .order_by(ResumeOptimization.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": item.id,
                "resume_id": item.resume_id,
                "job_title": item.job_title,
                "company_name": item.company_name,
                "ats_score": item.ats_score,
                "overall_score": item.overall_score,
                "created_at": item.created_at,
            }
            for item in items
        ]

    def _extract_resume_text(self, resume: Resume) -> str:
        metadata = resume.file_metadata or {}
        content = metadata.get("content")
        if isinstance(content, str) and content.strip():
            return content
        path = Path(resume.storage_path)
        if not path.exists():
            return ""
        return path.read_bytes().decode("utf-8", errors="ignore")

    def _parse_job_description(self, job_description: str) -> dict[str, Any]:
        text = job_description.strip()
        keywords = self._extract_keywords(text)
        skills = self._extract_skills_from_text(text)
        experience_requirement = self._extract_experience_requirement(text)
        education_requirements = self._extract_education_requirements(text)
        return {
            "keywords": keywords[:30],
            "skills": skills[:20],
            "experience_requirement": experience_requirement,
            "education_requirements": education_requirements,
            "job_title": self._guess_job_title(text),
            "company_name": self._guess_company_name(text),
            "responsibilities": self._split_points(text)[:8],
        }

    def _build_user_inventory(self, resume: Resume, profile: Profile | None, resume_text: str) -> dict[str, Any]:
        skills: set[str] = set()
        certifications: set[str] = set()
        education: set[str] = set()
        projects: list[str] = []
        technologies: set[str] = set()

        if profile:
            for skill in profile.skills or []:
                if isinstance(skill, str):
                    skills.add(self._normalize_term(skill))
            for cert in profile.certifications or []:
                if isinstance(cert, dict) and cert.get("name"):
                    certifications.add(self._normalize_term(str(cert["name"])))
            for edu in profile.education or []:
                if isinstance(edu, dict):
                    degree = edu.get("degree") or edu.get("field") or edu.get("institution")
                    if degree:
                        education.add(self._normalize_term(str(degree)))
            for project in profile.projects or []:
                if isinstance(project, dict) and project.get("name"):
                    projects.append(str(project["name"]))
                    desc = project.get("description", "")
                    if isinstance(desc, str):
                        for term in self._extract_skills_from_text(desc):
                            technologies.add(self._normalize_term(term))

        metadata = resume.file_metadata or {}
        experience_years = metadata.get("experience_years", 0)
        if isinstance(experience_years, str):
            try:
                experience_years = int(experience_years)
            except ValueError:
                experience_years = 0

        resume_skills = self._extract_skills_from_text(resume_text)
        for term in resume_skills:
            skills.add(self._normalize_term(term))
            technologies.add(self._normalize_term(term))

        for cert_match in re.findall(r"(?:certified|certification)\s+[\w\s]+", resume_text, re.IGNORECASE):
            certifications.add(self._normalize_term(cert_match))
        for edu_match in re.findall(r"(?:bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?tech|m\.?tech|mba|degree)", resume_text, re.IGNORECASE):
            education.add(self._normalize_term(edu_match))

        return {
            "skills": skills,
            "skills_display": {self._normalize_term(s): s for s in (profile.skills or []) if isinstance(s, str)},
            "certifications": certifications,
            "education": education,
            "projects": projects,
            "technologies": technologies,
            "experience_years": experience_years if isinstance(experience_years, (int, float)) else 0,
            "resume_text": resume_text.lower(),
        }

    def _compare_keywords(self, jd_keywords: list[str], resume_text: str, inventory: dict[str, Any]) -> tuple[list[str], list[str]]:
        resume_lower = resume_text.lower()
        matched: list[str] = []
        missing: list[str] = []
        for kw in jd_keywords:
            norm = self._normalize_term(kw)
            if not norm or len(norm) < 2:
                continue
            if norm in inventory["skills"] or norm in inventory["technologies"] or kw.lower() in resume_lower:
                matched.append(kw)
            else:
                missing.append(kw)
        return matched, missing

    def _compare_skills(self, jd_skills: list[str], inventory: dict[str, Any]) -> tuple[list[str], list[str]]:
        matched: list[str] = []
        missing: list[str] = []
        user_skills = inventory["skills"] | inventory["technologies"]
        for skill in jd_skills:
            norm = self._normalize_term(skill)
            if norm in user_skills:
                matched.append(skill)
            else:
                missing.append(skill)
        return matched, missing

    def _percentage_score(self, matched: int, total: int) -> float:
        if total <= 0:
            return 75.0
        return round(min(100.0, (matched / total) * 100), 1)

    def _experience_score(self, requirement: str | None, inventory: dict[str, Any]) -> float:
        years = inventory.get("experience_years", 0)
        if not requirement:
            return 85.0 if years > 0 else 70.0
        req = requirement.lower()
        if "fresher" in req or "0-2" in req or "entry" in req:
            return 100.0 if years <= 2 else max(60.0, 100.0 - (years - 2) * 10)
        if "2-4" in req or "mid" in req:
            if years >= 2:
                return min(100.0, 70.0 + years * 5)
            return max(40.0, years * 35)
        if "4+" in req or "senior" in req or "5+" in req:
            return min(100.0, 50.0 + years * 10) if years >= 4 else max(30.0, years * 15)
        return 80.0

    def _education_score(self, requirements: list[str], inventory: dict[str, Any]) -> float:
        if not requirements:
            return 100.0 if inventory["education"] else 85.0
        user_edu = inventory["education"]
        if not user_edu:
            return 50.0
        matched = 0
        for req in requirements:
            norm_req = self._normalize_term(req)
            if any(norm_req in edu or edu in norm_req for edu in user_edu):
                matched += 1
        return self._percentage_score(matched, len(requirements))

    def _compute_ats_score(self, keyword_match: float, skill_match: float, resume_text: str, keywords: list[str]) -> float:
        content = resume_text.lower()
        inline_matches = sum(1 for kw in keywords if kw.lower() in content)
        inline_ratio = inline_matches / max(1, len(keywords))
        base = 50.0 + inline_ratio * 30.0 + (keyword_match * 0.1) + (skill_match * 0.1)
        return round(min(100.0, max(40.0, base)), 1)

    def _build_recommendations(
        self,
        matched_keywords: list[str],
        missing_keywords: list[str],
        matched_skills: list[str],
        missing_skills: list[str],
        keyword_match: float,
        skill_match: float,
    ) -> list[str]:
        recommendations: list[str] = []
        if missing_keywords:
            recommendations.append(
                f"Incorporate these ATS keywords naturally where your experience supports them: {', '.join(missing_keywords[:5])}."
            )
        if missing_skills:
            recommendations.append(
                f"Highlight adjacent experience for role-critical skills: {', '.join(missing_skills[:4])}. "
                "Only add skills you genuinely possess."
            )
        if keyword_match < 70:
            recommendations.append("Mirror job-description terminology in your summary and experience bullets.")
        if skill_match < 70:
            recommendations.append("Reorder your skills section to prioritize matched competencies near the top.")
        if matched_keywords:
            recommendations.append(f"Strong keyword coverage includes: {', '.join(matched_keywords[:5])}.")
        if matched_skills:
            recommendations.append(f"Your resume already demonstrates: {', '.join(matched_skills[:5])}.")
        recommendations.extend([
            "Use concise bullet points with measurable outcomes.",
            "Keep section headings standard (Summary, Experience, Skills, Education).",
            "Avoid graphics or tables that ATS parsers may skip.",
        ])
        return recommendations[:10]

    def _generate_tailored_resume(
        self,
        resume_text: str,
        user_inventory: dict[str, Any],
        jd_analysis: dict[str, Any],
        matched_skills: list[str],
        missing_keywords: list[str],
        job_title: str | None,
        company_name: str | None,
    ) -> str:
        """Produce an improved resume using only verified user data — never invent credentials."""
        title_line = job_title or "Target Role"
        company_line = company_name or "Target Company"
        verified_skills = matched_skills[:12] or [
            user_inventory["skills_display"].get(norm, norm)
            for norm in sorted(list(user_inventory["skills"]))[:12]
        ]
        projects = user_inventory["projects"][:4]
        keywords_to_weave = [kw for kw in missing_keywords if self._keyword_supported(kw, user_inventory)][:6]

        sections = [
            f"# Optimized Resume — {title_line}",
            f"**Tailored for:** {company_line}",
            "",
            "## Professional Summary",
            self._build_summary(resume_text, verified_skills, jd_analysis.get("responsibilities", [])),
            "",
            "## Core Skills",
            *(f"- {skill}" for skill in verified_skills),
            "",
            "## Experience Highlights",
            *self._extract_experience_bullets(resume_text),
            "",
        ]

        if keywords_to_weave:
            sections.extend([
                "## ATS Keyword Integration",
                *(f"- Naturally emphasize '{kw}' in relevant experience bullets." for kw in keywords_to_weave),
                "",
            ])

        if projects:
            sections.extend(["## Relevant Projects", *(f"- {project}" for project in projects), ""])

        if user_inventory["education"]:
            sections.extend([
                "## Education",
                *(f"- {edu}" for edu in sorted(user_inventory["education"])[:4]),
                "",
            ])

        sections.extend([
            "## Source Resume Reference",
            resume_text.strip()[:1500] + ("..." if len(resume_text) > 1500 else ""),
        ])
        return "\n".join(sections)

    def _keyword_supported(self, keyword: str, inventory: dict[str, Any]) -> bool:
        norm = self._normalize_term(keyword)
        return norm in inventory["skills"] or norm in inventory["technologies"] or keyword.lower() in inventory["resume_text"]

    def _build_summary(self, resume_text: str, skills: list[str], responsibilities: list[str]) -> str:
        first_lines = [line.strip() for line in resume_text.splitlines() if line.strip()][:3]
        base = " ".join(first_lines)[:300] if first_lines else "Experienced professional with a proven track record."
        skill_phrase = ", ".join(skills[:5]) if skills else "relevant technical skills"
        return f"{base} Skilled in {skill_phrase}, with focus on delivering measurable outcomes aligned to the target role."

    def _extract_experience_bullets(self, resume_text: str) -> list[str]:
        bullets: list[str] = []
        for line in resume_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("-", "•", "*")) or re.match(r"^\d+\.", stripped):
                bullets.append(stripped.lstrip("-•* ").strip())
            elif len(stripped) > 30 and any(word in stripped.lower() for word in ("developed", "built", "led", "managed", "implemented", "designed")):
                bullets.append(stripped)
        if not bullets:
            chunks = [c.strip() for c in re.split(r"[\n.;]+", resume_text) if len(c.strip()) > 25]
            bullets = chunks[:5]
        return [f"- {bullet}" for bullet in bullets[:6]]

    def _store_output_files(self, record: ResumeOptimization, content: str) -> dict[str, str]:
        prefix = f"user_{record.user_id}_opt_{record.id}"
        pdf_path = OPTIMIZED_RESUME_DIR / f"{prefix}.pdf"
        docx_path = OPTIMIZED_RESUME_DIR / f"{prefix}.docx"
        pdf_path.write_bytes(content.encode("utf-8"))
        docx_path.write_bytes(content.encode("utf-8"))
        return {"pdf_path": str(pdf_path), "docx_path": str(docx_path)}

    def _to_analyze_response(self, record: ResumeOptimization) -> dict[str, Any]:
        breakdown = record.score_breakdown or {}
        return {
            "id": record.id,
            "ats_score": record.ats_score,
            "overall_score": record.overall_score,
            "keyword_match": breakdown.get("keyword_match", 0.0),
            "skill_match": breakdown.get("skill_match", 0.0),
            "experience_match": breakdown.get("experience_match", 0.0),
            "education_match": breakdown.get("education_match", 0.0),
            "matched_keywords": record.matched_keywords or [],
            "missing_keywords": record.missing_keywords or [],
            "matched_skills": record.matched_skills or [],
            "missing_skills": record.missing_skills or [],
            "recommendations": record.recommendations or [],
            "tailored_resume": record.tailored_resume or "",
        }

    def _to_read_response(self, record: ResumeOptimization) -> dict[str, Any]:
        breakdown = record.score_breakdown or {}
        return {
            "id": record.id,
            "user_id": record.user_id,
            "resume_id": record.resume_id,
            "job_title": record.job_title,
            "company_name": record.company_name,
            "ats_score": record.ats_score,
            "overall_score": record.overall_score,
            "keyword_match": breakdown.get("keyword_match", 0.0),
            "skill_match": breakdown.get("skill_match", 0.0),
            "experience_match": breakdown.get("experience_match", 0.0),
            "education_match": breakdown.get("education_match", 0.0),
            "matched_keywords": record.matched_keywords or [],
            "missing_keywords": record.missing_keywords or [],
            "matched_skills": record.matched_skills or [],
            "missing_skills": record.missing_skills or [],
            "recommendations": record.recommendations or [],
            "tailored_resume": record.tailored_resume,
            "created_at": record.created_at,
        }

    def _extract_keywords(self, text: str) -> list[str]:
        words = [w.strip() for w in re.split(r"[^A-Za-z0-9+#.]+", text) if w.strip()]
        result: list[str] = []
        for word in words:
            if len(word) < 3 or word.lower() in _NOISE_WORDS:
                continue
            if word not in result:
                result.append(word)
        for tech in _TECH_PATTERNS:
            if tech in text.lower() and tech.title() not in result and tech.upper() not in result:
                result.append(tech.title() if tech.isalpha() else tech.upper())
        return result

    def _extract_skills_from_text(self, text: str) -> list[str]:
        text_lower = text.lower()
        found: list[str] = []
        for tech in _TECH_PATTERNS:
            if tech in text_lower:
                display = tech.title() if tech.isalpha() else tech.upper()
                if display not in found:
                    found.append(display)
        for kw in self._extract_keywords(text):
            if len(kw) >= 3 and kw[0].isupper() and kw not in found:
                found.append(kw)
        return found[:25]

    def _extract_experience_requirement(self, text: str) -> str | None:
        patterns = [
            r"(\d+\+?\s*(?:-\s*\d+)?\s*years?(?:\s+of)?\s+experience)",
            r"(entry[\s-]level|mid[\s-]level|senior[\s-]level|fresher|junior|lead)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_education_requirements(self, text: str) -> list[str]:
        requirements: list[str] = []
        patterns = [
            r"bachelor'?s?\s+(?:degree\s+)?(?:in\s+)?[\w\s]+",
            r"master'?s?\s+(?:degree\s+)?(?:in\s+)?[\w\s]+",
            r"b\.?tech|m\.?tech|mba|ph\.?d",
        ]
        for pattern in patterns:
            for match in re.findall(pattern, text, re.IGNORECASE):
                if match not in requirements:
                    requirements.append(match.strip())
        return requirements[:5]

    def _guess_job_title(self, text: str) -> str | None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None
        first = lines[0]
        if len(first) < 80 and not first.endswith("."):
            return first
        match = re.search(r"(?:position|role|title)\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        return match.group(1).strip()[:120] if match else None

    def _guess_company_name(self, text: str) -> str | None:
        match = re.search(r"(?:company|organization|employer)\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip().splitlines()[0][:120]
        match = re.search(r"at\s+([A-Z][A-Za-z0-9&\s]{2,40})", text)
        return match.group(1).strip() if match else None

    def _split_points(self, text: str) -> list[str]:
        return [chunk.strip() for chunk in re.split(r"[\n.;]+", text or "") if chunk.strip()]

    def _normalize_term(self, term: str) -> str:
        return re.sub(r"[^a-z0-9+#]+", "", str(term).lower())
