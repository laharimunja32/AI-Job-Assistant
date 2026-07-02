"""Backend tests for Interview Feedback service (Milestone 18 Phase 1)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import create_app
from app.core.security import create_access_token
from app.db.models.interview import InterviewPreparation  # noqa: F401
from app.db.session import get_db
from app.services.interview_feedback_service import InterviewFeedbackService
from app.tests.test_interviews import TestingSessionLocal, _complete_preparation, _seed, setup_module

setup_module()


def _complete_session(client, headers, preparation_id: int) -> None:
    start = client.post(f"/api/v1/interviews/{preparation_id}/start", headers=headers)
    assert start.status_code == 200

    detail = client.get(f"/api/v1/interviews/{preparation_id}", headers=headers)
    question_count = len(detail.json()["questions"])

    for index in range(question_count):
        answer = client.post(
            f"/api/v1/interviews/{preparation_id}/answer",
            headers=headers,
            json={
                "answer_text": f"My structured answer for question {index + 1} because it delivered measurable results.",
                "time_spent_seconds": 90,
            },
        )
        assert answer.status_code == 200


def _create_evaluated_feedback(client, headers, db, email: str) -> tuple[TestClient, dict[str, str], int, int]:
    user, job = _seed(db, email=email)
    token = create_access_token(subject=user.email, role=user.role)
    auth_headers = {"Authorization": f"Bearer {token}"}

    preparation_id = _complete_preparation(client, headers=auth_headers, job_id=job.id, db=db)
    start = client.post(f"/api/v1/interviews/{preparation_id}/start", headers=auth_headers)
    session_id = start.json()["session"]["id"]
    _complete_session(client, auth_headers, preparation_id)

    evaluate = client.post(
        "/api/v1/interview-feedback/evaluate",
        headers=auth_headers,
        json={"session_id": session_id},
    )
    assert evaluate.status_code == 200
    feedback_id = evaluate.json()["id"]
    return client, auth_headers, feedback_id, session_id


def _client_with_db(db) -> TestClient:
    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_interview_feedback_service_lifecycle() -> None:
    db = TestingSessionLocal()
    app = create_app()
    user, job = _seed(db, email="feedback-service@example.com")

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    preparation_id = _complete_preparation(client, headers, job.id, db)
    start = client.post(f"/api/v1/interviews/{preparation_id}/start", headers=headers)
    session_id = start.json()["session"]["id"]
    _complete_session(client, headers, preparation_id)

    service = InterviewFeedbackService(db=db)
    detail = service.evaluate(user, session_id)
    feedback_id = detail["id"]

    assert detail["overall_score"] is not None
    assert detail["grammar_score"] is not None
    assert detail["clarity_score"] is not None
    assert detail["problem_solving_score"] is not None
    assert detail["summary_feedback"]
    assert detail["question_reviews"]

    history = service.get_history(user)
    assert history["total"] >= 1
    assert any(item["id"] == feedback_id for item in history["items"])

    fetched = service.get_by_id(user, feedback_id)
    assert fetched is not None
    assert fetched["id"] == feedback_id

    progress = service.get_progress(user)
    assert progress["completed_interviews"] >= 1
    assert progress["latest_score"] is not None
    assert progress["score_trend"]

    legacy_feedback = client.get(f"/api/v1/interviews/{preparation_id}/feedback", headers=headers)
    assert legacy_feedback.status_code == 200
    assert legacy_feedback.json()["overall_score"] is not None
    assert legacy_feedback.json()["grammar_score"] is not None

    service.delete(user, feedback_id)
    assert service.get_by_id(user, feedback_id) is None

    app.dependency_overrides.clear()
    db.close()


def test_milestone_17_feedback_includes_enhanced_scores() -> None:
    db = TestingSessionLocal()
    user, job = _seed(db, email="feedback-scores@example.com")

    app = create_app()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token(subject=user.email, role=user.role)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    preparation_id = _complete_preparation(client, headers, job.id, db)
    _complete_session(client, headers, preparation_id)

    finish = client.post(f"/api/v1/interviews/{preparation_id}/finish", headers=headers)
    assert finish.status_code == 200
    payload = finish.json()["feedback"]
    assert payload["grammar_score"] is not None
    assert payload["clarity_score"] is not None
    assert payload["problem_solving_score"] is not None
    assert payload["summary_feedback"]

    app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_endpoints_require_authentication() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)

    assert client.post("/api/v1/interview-feedback/evaluate", json={"session_id": 1}).status_code == 401
    assert client.get("/api/v1/interview-feedback/history").status_code == 401
    assert client.get("/api/v1/interview-feedback/progress").status_code == 401
    assert client.get("/api/v1/interview-feedback/1").status_code == 401
    assert client.delete("/api/v1/interview-feedback/1").status_code == 401

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_evaluate_endpoint() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, headers, feedback_id, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-evaluate@example.com"
    )

    assert feedback_id > 0

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_history_endpoint_pagination() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, headers, feedback_id, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-history@example.com"
    )

    page_one = client.get("/api/v1/interview-feedback/history?page=1&size=1", headers=headers)
    assert page_one.status_code == 200
    payload = page_one.json()
    assert payload["total"] >= 1
    assert payload["page"] == 1
    assert payload["size"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["id"] == feedback_id

    page_two = client.get("/api/v1/interview-feedback/history?page=2&size=1", headers=headers)
    assert page_two.status_code == 200
    assert page_two.json()["page"] == 2
    assert len(page_two.json()["items"]) == 0

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_progress_endpoint() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, headers, _, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-progress@example.com"
    )

    response = client.get("/api/v1/interview-feedback/progress", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["completed_interviews"] >= 1
    assert payload["latest_score"] is not None
    assert payload["score_trend"]

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_get_by_id_endpoint() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, headers, feedback_id, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-detail@example.com"
    )

    response = client.get(f"/api/v1/interview-feedback/{feedback_id}", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == feedback_id
    assert payload["overall_score"] is not None
    assert payload["question_reviews"] is not None

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_delete_endpoint() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, headers, feedback_id, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-delete@example.com"
    )

    delete = client.delete(f"/api/v1/interview-feedback/{feedback_id}", headers=headers)
    assert delete.status_code == 204

    missing = client.get(f"/api/v1/interview-feedback/{feedback_id}", headers=headers)
    assert missing.status_code == 404

    client.app.dependency_overrides.clear()
    db.close()


def test_interview_feedback_other_user_returns_404() -> None:
    db = TestingSessionLocal()
    client = _client_with_db(db)
    _, owner_headers, feedback_id, _ = _create_evaluated_feedback(
        client, {}, db, email="feedback-owner@example.com"
    )

    other_user, _ = _seed(db, email="feedback-intruder@example.com")
    other_token = create_access_token(subject=other_user.email, role=other_user.role)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    get_response = client.get(f"/api/v1/interview-feedback/{feedback_id}", headers=other_headers)
    assert get_response.status_code == 404

    delete_response = client.delete(f"/api/v1/interview-feedback/{feedback_id}", headers=other_headers)
    assert delete_response.status_code == 404

    still_there = client.get(f"/api/v1/interview-feedback/{feedback_id}", headers=owner_headers)
    assert still_there.status_code == 200

    client.app.dependency_overrides.clear()
    db.close()
