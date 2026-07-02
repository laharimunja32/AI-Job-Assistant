from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.recruitment_monitoring import (
    AssessmentCreate,
    AssessmentListResponse,
    AssessmentRead,
    AssessmentUpdate,
    EmailEventRead,
    EmailListResponse,
    EmailProcessRequest,
    InterviewCreate,
    InterviewListResponse,
    InterviewRead,
    InterviewUpdate,
    NotificationHistoryListResponse,
    ReminderCreate,
    ReminderListResponse,
    ReminderRead,
    ReminderUpdate,
    TimelineResponse,
)
from app.services.recruitment_monitoring_service import RecruitmentMonitoringService

router = APIRouter(tags=["recruitment-monitoring"])


def get_monitoring_service(db: Session = Depends(get_db)) -> RecruitmentMonitoringService:
    return RecruitmentMonitoringService(db=db)


@router.get("/emails", response_model=EmailListResponse)
def list_emails(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> EmailListResponse:
    return EmailListResponse(**service.list_emails(current_user, page=page, size=size))


@router.get("/emails/{email_id}", response_model=EmailEventRead)
def get_email(
    email_id: int,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> EmailEventRead:
    item = service.get_email(current_user, email_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email event not found")
    return EmailEventRead.model_validate(item)


@router.post("/emails/process", response_model=EmailEventRead, status_code=status.HTTP_201_CREATED)
def process_email(
    payload: EmailProcessRequest,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> EmailEventRead:
    try:
        item = service.process_email(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return EmailEventRead.model_validate(item)


@router.get("/assessments", response_model=AssessmentListResponse)
def list_assessments(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_value: str | None = Query(default=None, alias="status"),
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> AssessmentListResponse:
    return AssessmentListResponse(**service.list_assessments(current_user, page=page, size=size, status=status_value))


@router.post("/assessments", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> AssessmentRead:
    return AssessmentRead.model_validate(service.create_assessment(current_user, payload))


@router.put("/assessments/{assessment_id}", response_model=AssessmentRead)
def update_assessment(
    assessment_id: int,
    payload: AssessmentUpdate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> AssessmentRead:
    try:
        item = service.update_assessment(current_user, assessment_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AssessmentRead.model_validate(item)


@router.get("/interviews", response_model=InterviewListResponse)
def list_interviews(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_value: str | None = Query(default=None, alias="status"),
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> InterviewListResponse:
    return InterviewListResponse(**service.list_interviews(current_user, page=page, size=size, status=status_value))


@router.post("/interviews", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
def create_interview(
    payload: InterviewCreate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> InterviewRead:
    return InterviewRead.model_validate(service.create_interview(current_user, payload))


@router.put("/interviews/{interview_id}", response_model=InterviewRead)
def update_interview(
    interview_id: int,
    payload: InterviewUpdate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> InterviewRead:
    try:
        item = service.update_interview(current_user, interview_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return InterviewRead.model_validate(item)


@router.get("/timeline/{application_id}", response_model=TimelineResponse)
def get_timeline(
    application_id: int,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> TimelineResponse:
    return TimelineResponse(**service.get_timeline(current_user, application_id))


@router.post("/reminders", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> ReminderRead:
    return ReminderRead.model_validate(service.create_reminder(current_user, payload))


@router.get("/reminders", response_model=ReminderListResponse)
def list_reminders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> ReminderListResponse:
    return ReminderListResponse(**service.list_reminders(current_user, page=page, size=size))


@router.put("/reminders/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> ReminderRead:
    try:
        item = service.update_reminder(current_user, reminder_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReminderRead.model_validate(item)


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: int,
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    try:
        service.delete_reminder(current_user, reminder_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notifications/history", response_model=NotificationHistoryListResponse)
def list_notification_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: RecruitmentMonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(get_current_active_user),
) -> NotificationHistoryListResponse:
    return NotificationHistoryListResponse(**service.list_notifications(current_user, page=page, size=size))
