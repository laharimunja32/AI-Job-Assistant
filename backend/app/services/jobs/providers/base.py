from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JobProvider(ABC):
    """Base interface for job discovery providers."""

    name: str = "base"

    @abstractmethod
    def search(self, keyword: str | None = None, location: str | None = None, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Return raw job payloads from the provider."""
