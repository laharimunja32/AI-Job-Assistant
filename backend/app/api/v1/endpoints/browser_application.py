from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.application_history import BrowserAutomationRecord
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.browser_application import (
    BrowserApplicationListResponse,
    BrowserApplicationRead,
    BrowserApplicationStartRequest,
    BrowserApplicationSubmitRequest,
)
from app.services.browser_application_service import BrowserApplicationService

router = APIRouter(prefix="/browser-application", tags=["browser-application"])


def _get_manager(request: Request):
    return getattr(request.app.state, "browser_manager", None)


def _to_read(record: BrowserAutomationRecord) -> BrowserApplicationRead:
    return BrowserApplicationRead(
        id=record.id,
        application_id=record.application_id,
        job_id=record.job_id,
        company_name=record.company_name,
        job_title=record.job_title,
        status=record.status,
        browser_session_id=record.browser_session_id,
        resume_id=record.resume_id,
        cover_letter_id=record.cover_letter_id,
        duration_seconds=record.duration_seconds,
        applied_date=record.applied_date,
        error_message=record.error_message,
        metadata=record.metadata_json or {},
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def get_browser_application_service(request: Request, db: Session = Depends(get_db)) -> BrowserApplicationService:
    return BrowserApplicationService(db=db, browser_manager=_get_manager(request))


@router.post("/start", response_model=BrowserApplicationRead, status_code=status.HTTP_201_CREATED, summary="Start browser application")
def start_application(
    payload: BrowserApplicationStartRequest,
    current_user: User = Depends(get_current_active_user),
    service: BrowserApplicationService = Depends(get_browser_application_service),
) -> BrowserApplicationRead:
    record = service.start_application(current_user, payload)
    return _to_read(record)


@router.post("/{record_id}/submit", response_model=BrowserApplicationRead, summary="Submit browser application")
def submit_application(
    record_id: int,
    payload: BrowserApplicationSubmitRequest,
    current_user: User = Depends(get_current_active_user),
    service: BrowserApplicationService = Depends(get_browser_application_service),
) -> BrowserApplicationRead:
    try:
        record = service.submit_application(current_user, record_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_read(record)


@router.get("/history", response_model=BrowserApplicationListResponse, summary="Get browser application history")
def get_application_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: BrowserApplicationService = Depends(get_browser_application_service),
) -> BrowserApplicationListResponse:
    result = service.get_history(current_user.id, page=page, size=size)
    return BrowserApplicationListResponse(
        items=[_to_read(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
    )


@router.get("/{record_id}", response_model=BrowserApplicationRead, summary="Get browser application details")
def get_application_detail(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    service: BrowserApplicationService = Depends(get_browser_application_service),
) -> BrowserApplicationRead:
    record = service.get_by_id(current_user.id, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser application record not found")
    return _to_read(record)
