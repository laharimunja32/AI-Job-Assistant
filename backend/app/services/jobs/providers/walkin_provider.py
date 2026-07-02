from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any


class WalkInProvider(ABC):
    """Base interface for walk-in discovery providers."""

    name: str = "walkin-base"

    @abstractmethod
    def search(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return raw walk-in event payloads from the provider."""


class SampleWalkInProvider(WalkInProvider):
    """A deterministic sample provider used for local development and tests."""

    name = "sample-walkin"

    def search(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        today = date.today()
        keyword = (keyword or "").strip().lower()
        location = (location or "Hyderabad").strip().lower()
        filters = filters or {}

        events = [
            {
                "company_name": "TCS",
                "job_role": "Software Engineer",
                "job_description": "Walk-in interview for software engineers with strong Python and FastAPI experience.",
                "venue": "TCS Building, HITECH City",
                "city": "Hyderabad",
                "state": "Telangana",
                "walk_in_date": today + timedelta(days=1),
                "walk_in_time": "10:00 AM",
                "registration_deadline": today,
                "eligibility": "Freshers and experienced candidates",
                "degree": "B.Tech/B.E",
                "branch": "CSE/IT/ECE",
                "passout_year": "2023-2025",
                "skills": ["Python", "FastAPI", "SQL"],
                "experience_required": "0-2 years",
                "documents_required": ["Resume", "Photo ID"],
                "contact_details": "walkins@tcs.example",
                "registration_url": "https://example.com/walkins/tcs",
                "source": self.name,
                "event_status": "Upcoming",
            },
            {
                "company_name": "Infosys",
                "job_role": "Data Analyst",
                "job_description": "Walk-in interview for analysts focused on data pipelines and reporting.",
                "venue": "Infosys Campus, Gachibowli",
                "city": "Hyderabad",
                "state": "Telangana",
                "walk_in_date": today,
                "walk_in_time": "09:30 AM",
                "registration_deadline": today - timedelta(days=1),
                "eligibility": "Graduates",
                "degree": "Any Graduate",
                "branch": "Any",
                "passout_year": "2022-2024",
                "skills": ["SQL", "Excel", "Power BI"],
                "experience_required": "1-3 years",
                "documents_required": ["Resume", "Certificates"],
                "contact_details": "recruitment@infosys.example",
                "registration_url": "https://example.com/walkins/infosys",
                "source": self.name,
                "event_status": "Today",
            },
        ]

        if keyword and keyword not in {"software", "data", "engineer", "analyst"}:
            return []
        if location and location not in {"hyderabad", "hitech city", "gachibowli"}:
            return []
        if filters.get("eligibility") and filters.get("eligibility").lower() not in {"freshers", "graduates"}:
            return []
        return events
