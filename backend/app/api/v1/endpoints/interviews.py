from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.interview import (
    InterviewAnswerCreate,
    InterviewAnswerRead,
    InterviewAnswerSubmitResponse,
    InterviewFeedbackRead,
    InterviewHistoryResponse,
    InterviewPreparationGenerateResponse,
    InterviewPreparationRead,
    InterviewQuestionRead,
    InterviewSessionFinishResponse,
    InterviewSessionProgress,
    InterviewSessionRead,
    InterviewSessionStartResponse,
    InterviewStatistics,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _serialize_preparation(service: InterviewService, user: User, preparation_id: int) -> InterviewPreparationRead:
    preparation = service.get_preparation(user, preparation_id)
    if preparation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview preparation not found")
    questions = service.get_questions(user, preparation_id)
    payload = InterviewPreparationRead.model_validate(preparation)
    return payload.model_copy(update={"questions": [InterviewQuestionRead.model_validate(q) for q in questions]})


@router.post("/generate/{job_id}", response_model=InterviewPreparationGenerateResponse, summary="Generate interview preparation for a job")
def generate_interview_preparation(
    job_id: int,
    application_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewPreparationGenerateResponse:
    service = InterviewService(db=db)
    try:
        payload = service.generate_for_job(current_user, job_id, application_id=application_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return InterviewPreparationGenerateResponse(**payload)


@router.get("/history", response_model=InterviewHistoryResponse, summary="Get interview practice history")
def get_interview_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewHistoryResponse:
    service = InterviewService(db=db)
    return InterviewHistoryResponse(**service.get_history(current_user, page=page, size=size))


@router.get("/statistics", response_model=InterviewStatistics, summary="Get interview practice statistics")
def get_interview_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewStatistics:
    service = InterviewService(db=db)
    return InterviewStatistics(**service.get_statistics(current_user))


@router.get("/{preparation_id}", response_model=InterviewPreparationRead, summary="Get interview preparation details")
def get_interview_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewPreparationRead:
    service = InterviewService(db=db)
    return _serialize_preparation(service, current_user, preparation_id)


@router.delete("/{preparation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete interview preparation")
def delete_interview_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = InterviewService(db=db)
    try:
        service.delete_preparation(current_user, preparation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{preparation_id}/start", response_model=InterviewSessionStartResponse, summary="Start interview practice session")
def start_interview_session(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewSessionStartResponse:
    service = InterviewService(db=db)
    try:
        payload = service.start_session(current_user, preparation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return InterviewSessionStartResponse(
        session=InterviewSessionRead.model_validate(payload["session"]),
        current_question=InterviewQuestionRead.model_validate(payload["current_question"]),
        progress=InterviewSessionProgress(**payload["progress"]),
    )


@router.post("/{preparation_id}/answer", response_model=InterviewAnswerSubmitResponse, summary="Submit answer for current question")
def submit_interview_answer(
    preparation_id: int,
    body: InterviewAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewAnswerSubmitResponse:
    service = InterviewService(db=db)
    try:
        payload = service.submit_answer(
            current_user,
            preparation_id,
            answer_text=body.answer_text,
            time_spent_seconds=body.time_spent_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return InterviewAnswerSubmitResponse(
        answer=InterviewAnswerRead.model_validate(payload["answer"]),
        session=InterviewSessionRead.model_validate(payload["session"]),
        next_question=InterviewQuestionRead.model_validate(payload["next_question"]) if payload["next_question"] else None,
        progress=InterviewSessionProgress(**payload["progress"]),
    )


@router.post("/{preparation_id}/finish", response_model=InterviewSessionFinishResponse, summary="Finish interview practice session")
def finish_interview_session(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewSessionFinishResponse:
    service = InterviewService(db=db)
    try:
        payload = service.finish_session(current_user, preparation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return InterviewSessionFinishResponse(
        session=InterviewSessionRead.model_validate(payload["session"]),
        feedback=InterviewFeedbackRead.model_validate(payload["feedback"]),
    )


@router.get("/{preparation_id}/feedback", response_model=InterviewFeedbackRead, summary="Get interview session feedback")
def get_interview_feedback(
    preparation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> InterviewFeedbackRead:
    service = InterviewService(db=db)
    feedback = service.get_feedback(current_user, preparation_id)
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview feedback not found")
    return InterviewFeedbackRead.model_validate(feedback)
