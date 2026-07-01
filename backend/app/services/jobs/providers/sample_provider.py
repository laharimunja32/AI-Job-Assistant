from __future__ import annotations

from typing import Any

from app.services.jobs.providers.base import JobProvider


class SampleJobProvider(JobProvider):
    """A deterministic sample provider used for local development and tests."""

    name = "sample"

    def search(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        keyword = (keyword or "python").strip().lower()
        location = (location or "Hyderabad").strip()
        filters = filters or {}

        jobs = [
            {
                "title": "Python Backend Engineer",
                "company": "Example Labs",
                "location": location,
                "description": "Build APIs and services with FastAPI and PostgreSQL.",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience": "0-2 years",
                "employment_type": "Full Time",
                "work_mode": filters.get("work_mode") or "Remote",
                "salary": "12-18 LPA",
                "apply_url": "https://example.com/jobs/python-backend-engineer",
                "source": self.name,
                "posted_date": "2026-07-01",
                "tags": ["fresher", "remote"],
            },
            {
                "title": "Data Engineer",
                "company": "DataWorks",
                "location": location,
                "description": "Work with pipelines and analytics platforms.",
                "skills": ["Python", "SQL"],
                "experience": "1-3 years",
                "employment_type": "Full Time",
                "work_mode": "Hybrid",
                "salary": "10-15 LPA",
                "apply_url": "https://example.com/jobs/data-engineer",
                "source": self.name,
                "posted_date": "2026-07-02",
                "tags": ["hybrid"],
            },
        ]

        if keyword and keyword not in {"python", "data", "engineer"}:
            return []
        return jobs
