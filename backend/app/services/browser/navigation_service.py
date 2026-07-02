from __future__ import annotations

import logging
import time

try:
    from playwright.sync_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
except Exception:  # pragma: no cover - optional in test env until dependency install
    class PlaywrightError(Exception):
        pass

    class PlaywrightTimeoutError(TimeoutError):
        pass

from app.core.config import settings
from app.db.models.browser_session import BrowserSession
from app.schemas.browser import BrowserPageMetadata
from app.services.browser.browser_manager import BrowserManager

logger = logging.getLogger(__name__)


class NavigationService:
    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager

    def open_apply_url(self, session: BrowserSession, apply_url: str) -> BrowserPageMetadata:
        page = self.browser_manager.get_page(session.session_id)
        if page is None:
            raise ValueError("Active browser page not found for session")

        started = time.perf_counter()
        initial_url = page.url or None
        try:
            page.goto(apply_url, wait_until="domcontentloaded", timeout=settings.playwright_timeout)
            page.wait_for_load_state("networkidle", timeout=settings.playwright_timeout)
            navigation_ms = int((time.perf_counter() - started) * 1000)
            final_url = page.url or apply_url
            metadata = BrowserPageMetadata(
                title=page.title(),
                final_url=final_url,
                redirected=bool(initial_url and initial_url != final_url),
                navigation_time_ms=navigation_ms,
            )
            logger.info(
                "navigation_success session_id=%s browser=%s nav_ms=%s final_url=%s",
                session.session_id,
                session.browser_type,
                metadata.navigation_time_ms,
                metadata.final_url,
            )
            return metadata
        except PlaywrightTimeoutError as exc:
            logger.exception("Navigation timeout for session %s: %s", session.session_id, exc)
            raise TimeoutError("Navigation timed out") from exc
        except PlaywrightError as exc:
            logger.exception("Navigation failed for session %s: %s", session.session_id, exc)
            raise RuntimeError(f"Navigation failed: {exc}") from exc
