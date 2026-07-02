from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationFavoriteUpdate,
    ApplicationHistoryResponse,
    ApplicationListResponse,
    ApplicationNotesUpdate,
    ApplicationPriorityUpdate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    try:
        item = service.create(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return service.serialize_application(current_user, item)


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_value: str | None = Query(default=None, alias="status"),
    company: str | None = None,
    job_title: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = None,
    favorites_only: bool = False,
    sort_by: str = "updated_at",
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationListResponse:
    service = ApplicationService(db=db)
    return ApplicationListResponse(
        **service.list(
            current_user,
            page=page,
            size=size,
            status=status_value,
            company=company,
            job_title=job_title,
            start_date=start_date,
            end_date=end_date,
            search=search,
            favorites_only=favorites_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    )


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    item = service.get(current_user, application_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return service.serialize_application(current_user, item)


@router.put("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    try:
        item = service.update(current_user, application_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return service.serialize_application(current_user, item)


@router.patch("/{application_id}/favorite", response_model=ApplicationRead)
def update_favorite(
    application_id: int,
    payload: ApplicationFavoriteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    try:
        item = service.update(current_user, application_id, ApplicationUpdate(is_favorite=payload.is_favorite))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return service.serialize_application(current_user, item)


@router.patch("/{application_id}/notes", response_model=ApplicationRead)
def update_notes(
    application_id: int,
    payload: ApplicationNotesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    try:
        item = service.update(current_user, application_id, ApplicationUpdate(notes=payload.notes))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return service.serialize_application(current_user, item)


@router.patch("/{application_id}/priority", response_model=ApplicationRead)
def update_priority(
    application_id: int,
    payload: ApplicationPriorityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationRead:
    service = ApplicationService(db=db)
    try:
        item = service.update(current_user, application_id, ApplicationUpdate(priority=payload.priority))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return service.serialize_application(current_user, item)


@router.get("/{application_id}/history", response_model=ApplicationHistoryResponse)
def get_application_history(
    application_id: int,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApplicationHistoryResponse:
    service = ApplicationService(db=db)
    try:
        payload = service.history(current_user, application_id, page=page, size=size)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApplicationHistoryResponse(**payload)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = ApplicationService(db=db)
    try:
        service.delete(current_user, application_id, soft_delete=not hard_delete)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
