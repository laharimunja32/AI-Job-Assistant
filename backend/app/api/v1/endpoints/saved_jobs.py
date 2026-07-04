from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.saved_job import SavedJobCreate, SavedJobListResponse, SavedJobRead, SavedJobStatusResponse
from app.services.saved_job_service import SavedJobService

router = APIRouter(prefix="/saved-jobs", tags=["saved-jobs"])


def get_saved_job_service(db: Session = Depends(get_db)) -> SavedJobService:
    return SavedJobService(db=db)


@router.post("", response_model=SavedJobRead, status_code=status.HTTP_201_CREATED, summary="Save a job")
def save_job(
    payload: SavedJobCreate,
    current_user: User = Depends(get_current_active_user),
    service: SavedJobService = Depends(get_saved_job_service),
) -> SavedJobRead:
    record = service.save_job(current_user.id, payload)
    return SavedJobRead.model_validate(record)


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a saved job")
def remove_saved_job(
    saved_job_id: int,
    current_user: User = Depends(get_current_active_user),
    service: SavedJobService = Depends(get_saved_job_service),
) -> None:
    removed = service.remove_job(current_user.id, saved_job_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")


@router.get("", response_model=SavedJobListResponse, summary="Get saved jobs")
def list_saved_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: SavedJobService = Depends(get_saved_job_service),
) -> SavedJobListResponse:
    result = service.list_saved_jobs(current_user.id, page=page, size=size)
    return SavedJobListResponse(
        items=[SavedJobRead.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
    )


@router.get("/status/check", response_model=SavedJobStatusResponse, summary="Check if a job is saved")
def check_saved_status(
    job_id: int | None = Query(default=None),
    saved_job_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    service: SavedJobService = Depends(get_saved_job_service),
) -> SavedJobStatusResponse:
    return SavedJobStatusResponse(**service.check_saved_status(current_user.id, job_id=job_id, saved_job_id=saved_job_id))
