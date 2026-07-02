from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.cover_letter import (
    CoverLetterGenerateResponse,
    CoverLetterHistoryResponse,
    CoverLetterTemplateCreate,
    CoverLetterTemplateRead,
    CoverLetterTemplateUpdate,
    GeneratedCoverLetterRead,
)
from app.services.cover_letter_service import CoverLetterService

router = APIRouter(prefix="/cover-letters", tags=["cover-letters"])


@router.post("/generate/{job_id}", response_model=CoverLetterGenerateResponse)
def generate_cover_letter(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> CoverLetterGenerateResponse:
    service = CoverLetterService(db)
    try:
        return CoverLetterGenerateResponse(**service.generate_for_job(current_user, job_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/history", response_model=CoverLetterHistoryResponse)
def get_cover_letter_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoverLetterHistoryResponse:
    service = CoverLetterService(db)
    return CoverLetterHistoryResponse(**service.get_history(current_user, page, size))


@router.get("/{item_id}", response_model=GeneratedCoverLetterRead)
def get_cover_letter(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> GeneratedCoverLetterRead:
    service = CoverLetterService(db)
    item = service.get_cover_letter(current_user, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
    return GeneratedCoverLetterRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Response:
    service = CoverLetterService(db)
    try:
        service.delete_cover_letter(current_user, item_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{item_id}/download")
def download_cover_letter(
    item_id: int,
    format: str = Query(default="pdf"),  # noqa: A002
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = CoverLetterService(db)
    try:
        content, content_type, filename = service.download(current_user, item_id, format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/templates", response_model=list[CoverLetterTemplateRead])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> list[CoverLetterTemplateRead]:
    service = CoverLetterService(db)
    return [CoverLetterTemplateRead.model_validate(item) for item in service.list_templates(current_user)]


@router.post("/templates", response_model=CoverLetterTemplateRead)
def create_template(payload: CoverLetterTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> CoverLetterTemplateRead:
    service = CoverLetterService(db)
    return CoverLetterTemplateRead.model_validate(service.create_template(current_user, payload.model_dump()))


@router.put("/templates/{template_id}", response_model=CoverLetterTemplateRead)
def update_template(
    template_id: int,
    payload: CoverLetterTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoverLetterTemplateRead:
    service = CoverLetterService(db)
    try:
        item = service.update_template(current_user, template_id, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return CoverLetterTemplateRead.model_validate(item)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Response:
    service = CoverLetterService(db)
    try:
        service.delete_template(current_user, template_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
