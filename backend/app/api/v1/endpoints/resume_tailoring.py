from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.resume_tailoring import (
    ResumeGenerationHistoryResponse,
    TailoredResumeGenerateResponse,
    TailoredResumeRead,
)
from app.services.resume_tailoring_service import ResumeTailoringService

router = APIRouter(prefix="/resume-tailoring", tags=["resume-tailoring"])


@router.post("/generate/{job_id}", response_model=TailoredResumeGenerateResponse, summary="Generate a tailored resume for a job")
def generate_tailored_resume(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TailoredResumeGenerateResponse:
    service = ResumeTailoringService(db=db)
    try:
        payload = service.generate_for_job(current_user, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TailoredResumeGenerateResponse(**payload)


@router.get("/history", response_model=ResumeGenerationHistoryResponse, summary="Get resume generation history")
def get_resume_tailoring_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeGenerationHistoryResponse:
    service = ResumeTailoringService(db=db)
    return ResumeGenerationHistoryResponse(**service.get_history(current_user, page=page, size=size))


@router.get("/{tailored_id}", response_model=TailoredResumeRead, summary="Get tailored resume details")
def get_tailored_resume(
    tailored_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> TailoredResumeRead:
    service = ResumeTailoringService(db=db)
    item = service.get_tailored_resume(current_user, tailored_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tailored resume not found")
    return TailoredResumeRead.model_validate(item)


@router.delete("/{tailored_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete tailored resume and generated files")
def delete_tailored_resume(
    tailored_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = ResumeTailoringService(db=db)
    try:
        service.delete_tailored_resume(current_user, tailored_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{tailored_id}/download", summary="Download tailored resume in a selected format")
def download_tailored_resume(
    tailored_id: int,
    format: str = Query(default="pdf"),  # noqa: A002
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = ResumeTailoringService(db=db)
    try:
        content, content_type, filename = service.download(current_user, tailored_id, file_format=format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
