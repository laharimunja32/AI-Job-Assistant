from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class DashboardCache:
    """Simple in-memory TTL cache for dashboard responses."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def _key(self, namespace: str, user_id: int, suffix: str = "") -> str:
        return f"{namespace}:{user_id}:{suffix}"

    def get(self, namespace: str, user_id: int, suffix: str = "") -> Any | None:
        key = self._key(namespace, user_id, suffix)
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, namespace: str, user_id: int, value: Any, suffix: str = "") -> None:
        key = self._key(namespace, user_id, suffix)
        self._store[key] = (time.time() + self.ttl_seconds, value)

    def invalidate_user(self, user_id: int) -> None:
        prefix = f":{user_id}:"
        keys_to_delete = [key for key in self._store if prefix in key]
        for key in keys_to_delete:
            del self._store[key]

    def clear(self) -> None:
        self._store.clear()
