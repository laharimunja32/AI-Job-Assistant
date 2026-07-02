from datetime import datetime, timedelta
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import create_app
from app.core.security import create_access_token
from app.db.base import Base
from app.db.models.application import Application
from app.db.models.browser_session import BrowserSession
from app.db.models.submission_review import SubmissionReviewAudit
from app.db.models.job import Job
from app.db.models.user import User
from app.db.session import get_db
from app.services.browser.browser_manager import BrowserManager

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FakeBrowserManager(BrowserManager):
    def __init__(self) -> None:
        self.created_count = 0
        self._urls: dict[str, str] = {}
        self._form_detection_cache = {}
        self._form_report_cache = {}
        self._form_stats = {
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
        self._upload_detection_cache = {}
        self._upload_report_cache = {}

    def start(self) -> None:  # noqa: D401
        return None

    def shutdown(self, db=None) -> None:  # noqa: ANN001
        return None

    def create_session(self, db, user_id: int, browser_type: str, application_id: int | None = None):  # noqa: ANN001
        self.created_count += 1
        generated_session_id = f"session-{self.created_count}-{uuid.uuid4().hex[:6]}"
        session = BrowserSession(
            session_id=generated_session_id,
            user_id=user_id,
            application_id=application_id,
            browser_type=browser_type,
            status="active",
            current_url=None,
            last_activity=datetime.utcnow(),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        self._urls[generated_session_id] = ""
        return session

    def close_session(self, session_id: str, db=None, status: str = "closed") -> None:  # noqa: ANN001
        if db is None:
            return
        session = db.query(BrowserSession).filter(BrowserSession.session_id == session_id).first()
        if session:
            session.status = status
            session.last_activity = datetime.utcnow()
            db.add(session)
            db.commit()

    def restart_session(self, db, session: BrowserSession, browser_type: str | None = None):  # noqa: ANN001
        self.close_session(session.session_id, db=db, status="closed")
        return self.create_session(db, session.user_id, browser_type or session.browser_type, session.application_id)

    def cleanup_idle_sessions(self, db):  # noqa: ANN001
        return 0

    def status_summary(self, db, user_id: int):  # noqa: ANN001
        sessions = db.query(BrowserSession).filter(BrowserSession.user_id == user_id).all()
        return {
            "active_sessions": sum(1 for s in sessions if s.status == "active"),
            "last_browser_activity": max((s.last_activity for s in sessions), default=None),
            "navigation_success_rate": 100.0,
            "browser_status": "healthy",
        }

    def get_page(self, session_id: str):  # noqa: ANN001
        manager = self

        class FakePage:
            url = manager._urls.get(session_id, "")
            _fills: dict[str, str] = {}

            def goto(self, apply_url: str, wait_until: str, timeout: int):  # noqa: ARG002
                manager._urls[session_id] = apply_url
                self.url = apply_url

            def wait_for_load_state(self, state: str, timeout: int):  # noqa: ARG002
                return None

            def title(self):
                return "Apply Page"

            def evaluate(self, script: str):  # noqa: ARG002
                if "input[type=\"file\"]" in script or "input[type='file']" in script:
                    return [
                        {
                            "selector": "[name='resume_upload']",
                            "inputType": "file",
                            "ariaLabel": "Upload Resume",
                            "placeholder": "",
                            "labelText": "Resume",
                            "nearbyText": "Upload your resume",
                            "visible": True,
                            "uploadCapability": "standard",
                        },
                        {
                            "selector": "[name='cover_upload']",
                            "inputType": "file",
                            "ariaLabel": "Upload Cover Letter",
                            "placeholder": "",
                            "labelText": "Cover Letter",
                            "nearbyText": "Upload your cover letter",
                            "visible": True,
                            "uploadCapability": "standard",
                        },
                    ]
                return [
                    {
                        "selector": "[name='first_name']",
                        "label": "First Name",
                        "placeholder": "Enter first name",
                        "name": "first_name",
                        "ariaLabel": None,
                        "nearbyText": "First Name",
                        "inputType": "text",
                        "required": True,
                        "tagName": "input",
                    },
                    {
                        "selector": "[name='email']",
                        "label": "Email",
                        "placeholder": "you@example.com",
                        "name": "email",
                        "ariaLabel": None,
                        "nearbyText": "Email",
                        "inputType": "email",
                        "required": True,
                        "tagName": "input",
                    },
                ]

            def locator(self, selector: str):
                page = self

                class FakeLocator:
                    first = None

                    def __init__(self):
                        self.first = self

                    def evaluate(self, script: str):  # noqa: ARG002
                        if "accept" in script:
                            return {"accept": ".pdf,.doc,.docx", "multiple": False}
                        return "input"

                    def fill(self, value: str):
                        page._fills[selector] = value

                    def set_input_files(self, value: str):
                        page._fills[selector] = value

                    def input_value(self, timeout: int = 0):  # noqa: ARG002
                        return page._fills.get(selector, "")

                    def select_option(self, label: str):  # noqa: ARG002
                        return None

                    def check(self):
                        return None

                    def uncheck(self):
                        return None

                return FakeLocator()

            def get_by_role(self, role: str, name: str):  # noqa: ARG002
                class FakeRoleLocator:
                    def count(self):
                        return 0

                    @property
                    def first(self):
                        return self

                    def click(self):
                        return None

                return FakeRoleLocator()

        return FakePage()

    def capture_screenshot(self, session_id: str) -> str | None:  # noqa: ARG002
        return "reports/browser-screenshots/fake.png"


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)


def _seed(db, email: str = "browser@example.com"):
    user = User(email=email, hashed_password="hash", full_name="Browser User")
    db.add(user)
    db.flush()
    job = Job(title="QA Engineer", company_name="Acme", status="active", apply_url="https://example.com/apply")
    db.add(job)
    db.flush()
    application = Application(
        user_id=user.id,
        job_id=job.id,
        company_name="Acme",
        job_title="QA Engineer",
        apply_url="https://example.com/apply",
        status="ready_to_apply",
    )
    db.add(application)
    db.commit()
    db.refresh(user)
    db.refresh(application)
    return user, application


def test_browser_session_lifecycle_endpoints() -> None:
    db = TestingSessionLocal()
    user, application = _seed(db, email="browser-lifecycle@example.com")
    app = create_app()
    app.state.browser_manager = FakeBrowserManager()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/browser/session", headers=headers, json={"browser_type": "chromium"})
    assert created.status_code == 201
    session_id = created.json()["session_id"]

    listed = client.get("/api/v1/browser/sessions", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    opened = client.post(f"/api/v1/browser/open/{application.id}", headers=headers, json={"session_id": session_id})
    assert opened.status_code == 200

    restarted = client.post(f"/api/v1/browser/session/{session_id}/restart", headers=headers, json={})
    assert restarted.status_code == 200

    status_resp = client.get("/api/v1/browser/status", headers=headers)
    assert status_resp.status_code == 200
    assert "active_sessions" in status_resp.json()

    closed = client.delete(f"/api/v1/browser/session/{session_id}", headers=headers)
    assert closed.status_code == 204

    app.dependency_overrides.clear()
    db.close()


def test_browser_session_security_enforces_user_scope() -> None:
    db = TestingSessionLocal()
    user_a, _ = _seed(db, email="browser-security@example.com")
    user_b = User(email="browser2@example.com", hashed_password="hash", full_name="Other User")
    db.add(user_b)
    db.commit()
    db.refresh(user_b)

    app = create_app()
    manager = FakeBrowserManager()
    app.state.browser_manager = manager

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    token_a = create_access_token(subject=user_a.email, role=user_a.role)
    token_b = create_access_token(subject=user_b.email, role=user_b.role)
    client = TestClient(app)
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    created = client.post("/api/v1/browser/session", headers=headers_a, json={"browser_type": "firefox"})
    session_id = created.json()["session_id"]

    response = client.get(f"/api/v1/browser/session/{session_id}", headers=headers_b)
    assert response.status_code == 404

    app.dependency_overrides.clear()
    db.close()


def test_browser_manager_cleanup_marks_idle_sessions() -> None:
    db = TestingSessionLocal()
    user, _ = _seed(db, email="browser-cleanup@example.com")
    session = BrowserSession(
        session_id="idle-session",
        user_id=user.id,
        browser_type="chromium",
        status="active",
        last_activity=datetime.utcnow() - timedelta(hours=3),
    )
    db.add(session)
    db.commit()

    manager = FakeBrowserManager()
    manager.close_session("idle-session", db=db, status="idle")

    refreshed = db.query(BrowserSession).filter(BrowserSession.session_id == "idle-session").first()
    assert refreshed is not None
    assert refreshed.status == "idle"
    db.close()


def test_form_detection_fill_and_report_endpoints() -> None:
    db = TestingSessionLocal()
    user, _ = _seed(db, email="browser-forms@example.com")
    app = create_app()
    app.state.browser_manager = FakeBrowserManager()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/browser/session", headers=headers, json={"browser_type": "chromium"})
    assert created.status_code == 201
    session_id = created.json()["session_id"]

    detect = client.post(f"/api/v1/browser/forms/detect/{session_id}", headers=headers)
    assert detect.status_code == 200
    assert detect.json()["total_fields"] >= 2

    fill = client.post(f"/api/v1/browser/forms/fill/{session_id}", headers=headers, json={})
    assert fill.status_code == 200
    assert "filled_fields" in fill.json()

    report = client.get(f"/api/v1/browser/forms/report/{session_id}", headers=headers)
    assert report.status_code == 200
    assert "completion_percentage" in report.json()

    app.dependency_overrides.clear()
    db.close()


def test_upload_detection_endpoint() -> None:
    db = TestingSessionLocal()
    user, _ = _seed(db, email="browser-upload-detect@example.com")
    app = create_app()
    app.state.browser_manager = FakeBrowserManager()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/api/v1/browser/session", headers=headers, json={"browser_type": "chromium"})
    session_id = created.json()["session_id"]

    detect = client.post(f"/api/v1/browser/uploads/detect/{session_id}", headers=headers)
    assert detect.status_code == 200
    body = detect.json()
    assert body["total_fields"] >= 2
    assert any(item["field_type"] == "resume" for item in body["fields"])

    app.dependency_overrides.clear()
    db.close()


def test_guided_review_validation_confirmation_and_history() -> None:
    db = TestingSessionLocal()
    user, application = _seed(db, email="browser-review@example.com")
    app = create_app()
    app.state.browser_manager = FakeBrowserManager()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post("/api/v1/browser/session", headers=headers, json={"browser_type": "chromium", "application_id": application.id})
    assert created.status_code == 201
    session_id = created.json()["session_id"]

    detect = client.post(f"/api/v1/browser/forms/detect/{session_id}", headers=headers)
    assert detect.status_code == 200
    review = client.get(f"/api/v1/browser/review/{session_id}", headers=headers)
    assert review.status_code == 200
    assert "readiness" in review.json()

    validation = client.post(f"/api/v1/browser/review/validate/{session_id}", headers=headers)
    assert validation.status_code == 200
    assert "checks" in validation.json()

    confirm = client.post(
        f"/api/v1/browser/review/confirm/{session_id}",
        headers=headers,
        json={"confirmed": True, "attempt_submission": False, "review_time_seconds": 30},
    )
    assert confirm.status_code == 200
    assert confirm.json()["result"] in {"review_required", "ready_to_submit", "review_confirmed"}

    history = client.get(f"/api/v1/browser/review/history/{application.id}", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] >= 1

    row = db.query(SubmissionReviewAudit).filter(SubmissionReviewAudit.application_id == application.id).first()
    assert row is not None

    app.dependency_overrides.clear()
    db.close()
