from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.resume import ResumeListResponse, ResumeRead
from app.services.profile_service import (
    create_resume,
    delete_resume,
    download_resume,
    get_resume,
    list_resumes,
    set_active_resume,
)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post(
    "",
    response_model=ResumeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new master resume",
    response_description="Created resume metadata",
)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeRead:
    return create_resume(db, current_user, file)


@router.get("", response_model=ResumeListResponse, summary="List resumes for the current user")
def list_user_resumes(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    active: bool | None = Query(default=None),
    filename_contains: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeListResponse:
    items, total = list_resumes(db, current_user, page=page, size=size, active=active, filename_contains=filename_contains)
    return ResumeListResponse(items=items, total=total, page=page, size=size)


@router.get("/{resume_id}/download")
def download_user_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    resume = get_resume(db, current_user, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    content, content_type = download_resume(resume)
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": f"attachment; filename={resume.filename}"})


@router.post("/{resume_id}/activate", response_model=ResumeRead, summary="Set an uploaded resume as the active resume")
def activate_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeRead:
    return set_active_resume(db, current_user, resume_id)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a resume")
def delete_user_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    delete_resume(db, current_user, resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
