from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.browser_session import BrowserSession
from app.schemas.browser import BrowserEventLog, FormDetectionResponse, FormFillResponse, UploadDetectionResponse, UploadStatusResponse

try:
    from playwright.sync_api import Browser, BrowserContext, Error as PlaywrightError, Page, sync_playwright
except Exception:  # pragma: no cover - optional in test env until dependency install
    Browser = BrowserContext = Page = object  # type: ignore[assignment]

    class PlaywrightError(Exception):
        pass

    sync_playwright = None

logger = logging.getLogger(__name__)


@dataclass
class RuntimeSession:
    browser: Browser
    context: BrowserContext
    page: Page
    browser_type: str
    started_at: datetime
    launch_time_ms: int


class BrowserManager:
    def __init__(self) -> None:
        self._playwright = None
        self._sessions: dict[str, RuntimeSession] = {}
        self._form_detection_cache: dict[str, FormDetectionResponse] = {}
        self._form_report_cache: dict[str, FormFillResponse] = {}
        self._upload_detection_cache: dict[str, UploadDetectionResponse] = {}
        self._upload_report_cache: dict[str, UploadStatusResponse] = {}
        self._form_stats: dict[str, float] = {
            "forms_detected": 0,
            "fields_filled": 0,
            "manual_fields_remaining": 0,
            "fill_runs": 0,
            "average_fill_success_rate": 0.0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "resume_upload_count": 0,
            "cover_letter_upload_count": 0,
            "upload_runs": 0,
            "average_upload_time_ms": 0.0,
        }

    def start(self) -> None:
        if self._playwright is None:
            if sync_playwright is None:
                raise RuntimeError("Playwright is not installed. Run: pip install playwright")
            self._playwright = sync_playwright().start()

    def shutdown(self, db: Session | None = None) -> None:
        for session_id in list(self._sessions.keys()):
            self.close_session(session_id, db=db, status="closed")
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def create_session(self, db: Session, user_id: int, browser_type: str, application_id: int | None = None) -> BrowserSession:
        self.start()
        self.cleanup_idle_sessions(db)
        self._ensure_session_capacity(db)

        start = time.perf_counter()
        browser = self._launch_browser(browser_type)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        launch_ms = int((time.perf_counter() - start) * 1000)

        session_id = uuid.uuid4().hex
        runtime = RuntimeSession(
            browser=browser,
            context=context,
            page=page,
            browser_type=browser_type,
            started_at=datetime.utcnow(),
            launch_time_ms=launch_ms,
        )
        self._sessions[session_id] = runtime

        record = BrowserSession(
            session_id=session_id,
            user_id=user_id,
            application_id=application_id,
            browser_type=browser_type,
            status="active",
            current_url=page.url or None,
            last_activity=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        self._log_event(
            BrowserEventLog(
                browser_launch_time_ms=launch_ms,
                current_url=record.current_url,
                browser_type=browser_type,
            )
        )
        return record

    def get_page(self, session_id: str) -> Page | None:
        runtime = self._sessions.get(session_id)
        if runtime is None:
            return None
        return runtime.page

    def create_context(self, session_id: str) -> BrowserContext | None:
        runtime = self._sessions.get(session_id)
        if runtime is None:
            return None
        return runtime.browser.new_context(ignore_https_errors=True)

    def create_page(self, session_id: str) -> Page | None:
        context = self.create_context(session_id)
        if context is None:
            return None
        return context.new_page()

    def touch(self, db: Session, session: BrowserSession, current_url: str | None = None, error: str | None = None) -> BrowserSession:
        session.last_activity = datetime.utcnow()
        if current_url is not None:
            session.current_url = current_url
        if error:
            session.error_message = error
            session.status = "failed"
        elif session.status != "failed":
            session.status = "active"
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def close_session(self, session_id: str, db: Session | None = None, status: str = "closed") -> None:
        runtime = self._sessions.pop(session_id, None)
        if runtime:
            try:
                runtime.context.close()
                runtime.browser.close()
            except PlaywrightError as exc:
                logger.exception("Failed closing browser session %s: %s", session_id, exc)
        if db is not None:
            session = db.query(BrowserSession).filter(BrowserSession.session_id == session_id).first()
            if session:
                session.status = status
                session.last_activity = datetime.utcnow()
                db.add(session)
                db.commit()
        self._form_detection_cache.pop(session_id, None)
        self._form_report_cache.pop(session_id, None)
        self._upload_detection_cache.pop(session_id, None)
        self._upload_report_cache.pop(session_id, None)

    def get_form_detection(self, session_id: str) -> FormDetectionResponse | None:
        return self._form_detection_cache.get(session_id)

    def cache_form_detection(self, session_id: str, report: FormDetectionResponse) -> None:
        self._form_detection_cache[session_id] = report
        self._form_stats["forms_detected"] += 1

    def get_form_report(self, session_id: str) -> FormFillResponse | None:
        return self._form_report_cache.get(session_id)

    def cache_form_report(self, session_id: str, report: FormFillResponse) -> None:
        self._form_report_cache[session_id] = report
        self._form_stats["fields_filled"] += len(report.filled_fields)
        self._form_stats["manual_fields_remaining"] += len(report.required_manual_input)
        self._form_stats["fill_runs"] += 1
        runs = self._form_stats["fill_runs"]
        prev_avg = self._form_stats["average_fill_success_rate"]
        self._form_stats["average_fill_success_rate"] = round(
            ((prev_avg * (runs - 1)) + report.completion_percentage) / runs,
            1,
        )

    def form_stats_summary(self) -> dict[str, float]:
        return dict(self._form_stats)

    def get_upload_detection(self, session_id: str) -> UploadDetectionResponse | None:
        return self._upload_detection_cache.get(session_id)

    def cache_upload_detection(self, session_id: str, report: UploadDetectionResponse) -> None:
        self._upload_detection_cache[session_id] = report

    def get_upload_report(self, session_id: str) -> UploadStatusResponse | None:
        return self._upload_report_cache.get(session_id)

    def cache_upload_report(self, session_id: str, report: UploadStatusResponse) -> None:
        self._upload_report_cache[session_id] = report
        self._form_stats["upload_runs"] += 1
        success_count = len(report.uploaded_fields)
        fail_count = len(report.failed_fields)
        self._form_stats["successful_uploads"] += success_count
        self._form_stats["failed_uploads"] += fail_count
        self._form_stats["resume_upload_count"] += sum(1 for field in report.uploaded_fields if field.document_type in {"resume", "tailored_resume"})
        self._form_stats["cover_letter_upload_count"] += sum(1 for field in report.uploaded_fields if field.document_type == "cover_letter")
        run_duration = [field.duration_ms or 0 for field in report.uploaded_fields + report.failed_fields if field.duration_ms is not None]
        if run_duration:
            runs = self._form_stats["upload_runs"]
            avg_now = sum(run_duration) / len(run_duration)
            prev = self._form_stats["average_upload_time_ms"]
            self._form_stats["average_upload_time_ms"] = round(((prev * (runs - 1)) + avg_now) / runs, 1)

    def restart_session(self, db: Session, session: BrowserSession, browser_type: str | None = None) -> BrowserSession:
        self.close_session(session.session_id, db=db, status="closed")
        return self.create_session(
            db=db,
            user_id=session.user_id,
            browser_type=browser_type or session.browser_type,
            application_id=session.application_id,
        )

    def handle_crash(self, db: Session, session: BrowserSession, error: str) -> BrowserSession:
        self.close_session(session.session_id)
        session.status = "failed"
        session.error_message = error
        session.last_activity = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        self._log_event(
            BrowserEventLog(
                browser_type=session.browser_type,
                current_url=session.current_url,
                error=error,
            )
        )
        return session

    def cleanup_idle_sessions(self, db: Session) -> int:
        timeout = datetime.utcnow() - timedelta(seconds=settings.session_idle_timeout)
        idle_sessions = (
            db.query(BrowserSession)
            .filter(BrowserSession.status.in_(["active", "idle"]), BrowserSession.last_activity < timeout)
            .all()
        )
        for record in idle_sessions:
            self.close_session(record.session_id, db=db, status="idle")
        return len(idle_sessions)

    def status_summary(self, db: Session, user_id: int) -> dict:
        sessions = db.query(BrowserSession).filter(BrowserSession.user_id == user_id).all()
        active = sum(1 for s in sessions if s.status == "active")
        closed = sum(1 for s in sessions if s.status == "closed")
        failed = sum(1 for s in sessions if s.status == "failed")
        success_denominator = closed + failed
        success_rate = (closed / success_denominator) * 100 if success_denominator else 100.0
        last_activity = max((s.last_activity for s in sessions), default=None)
        browser_status = "healthy" if failed == 0 else "degraded"
        return {
            "active_sessions": active,
            "last_browser_activity": last_activity,
            "navigation_success_rate": round(success_rate, 1),
            "browser_status": browser_status,
        }

    def capture_screenshot(self, session_id: str) -> str | None:
        runtime = self._sessions.get(session_id)
        if runtime is None:
            return None
        output_dir = Path("reports/browser-screenshots")
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{session_id}-{int(time.time())}.png"
        runtime.page.screenshot(path=str(path), full_page=True)
        return str(path)

    def _launch_browser(self, browser_type: str) -> Browser:
        if self._playwright is None:
            self.start()
        if browser_type == "firefox":
            return self._playwright.firefox.launch(headless=settings.playwright_headless)
        if browser_type == "edge":
            return self._playwright.chromium.launch(channel="msedge", headless=settings.playwright_headless)
        return self._playwright.chromium.launch(headless=settings.playwright_headless)

    def _ensure_session_capacity(self, db: Session) -> None:
        running = db.query(BrowserSession).filter(BrowserSession.status == "active").count()
        if running >= settings.max_browser_sessions:
            raise ValueError(f"Maximum browser sessions reached ({settings.max_browser_sessions})")

    def _log_event(self, event: BrowserEventLog) -> None:
        logger.info(
            "browser_event browser=%s launch_ms=%s nav_ms=%s current_url=%s duration_s=%s error=%s",
            event.browser_type,
            event.browser_launch_time_ms,
            event.navigation_time_ms,
            event.current_url,
            event.session_duration_seconds,
            event.error,
        )
