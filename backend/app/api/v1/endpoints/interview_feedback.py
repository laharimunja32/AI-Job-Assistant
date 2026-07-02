from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.interview_feedback import (
    InterviewFeedbackDetailRead,
    InterviewFeedbackEvaluateRequest,
    InterviewFeedbackHistoryResponse,
    InterviewFeedbackProgressRead,
)
from app.services.interview_feedback_service import InterviewFeedbackService

router = APIRouter(prefix="/interview-feedback", tags=["interview-feedback"])


@router.post("/evaluate", response_model=InterviewFeedbackDetailRead, summary="Evaluate an interview session")
def evaluate_interview_feedback(
    body: InterviewFeedbackEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewFeedbackDetailRead:
    service = InterviewFeedbackService(db=db)
    try:
        payload = service.evaluate(current_user, body.session_id)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
    return InterviewFeedbackDetailRead(**payload)


@router.get("/history", response_model=InterviewFeedbackHistoryResponse, summary="Get interview feedback history")
def get_interview_feedback_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewFeedbackHistoryResponse:
    service = InterviewFeedbackService(db=db)
    return InterviewFeedbackHistoryResponse(**service.get_history(current_user, page=page, size=size))


@router.get("/progress", response_model=InterviewFeedbackProgressRead, summary="Get interview feedback progress")
def get_interview_feedback_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewFeedbackProgressRead:
    service = InterviewFeedbackService(db=db)
    return InterviewFeedbackProgressRead(**service.get_progress(current_user))


@router.get("/{feedback_id}", response_model=InterviewFeedbackDetailRead, summary="Get interview feedback by ID")
def get_interview_feedback_by_id(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewFeedbackDetailRead:
    service = InterviewFeedbackService(db=db)
    payload = service.get_by_id(current_user, feedback_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview feedback not found")
    return InterviewFeedbackDetailRead(**payload)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete interview feedback")
def delete_interview_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = InterviewFeedbackService(db=db)
    try:
        service.delete(current_user, feedback_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
