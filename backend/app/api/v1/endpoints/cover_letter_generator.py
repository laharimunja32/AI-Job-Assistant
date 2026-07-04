from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.cover_letter_generator import (
    CoverLetterDetail,
    CoverLetterHistoryItem,
    CoverLetterHistoryResponse,
    CoverLetterUpdateRequest,
    GenerateCoverLetterRequest,
    GenerateCoverLetterResponse,
)
from app.services.cover_letter_generator_service import CoverLetterGeneratorService

router = APIRouter(prefix="/cover-letter-generator", tags=["cover-letter-generator"])


@router.post("/generate", response_model=GenerateCoverLetterResponse)
def generate_cover_letter(
    payload: GenerateCoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GenerateCoverLetterResponse:
    service = CoverLetterGeneratorService(db)
    try:
        result = service.generate(
            current_user,
            payload.resume_id,
            payload.job_description,
            payload.job_title,
            payload.company_name,
            template_name=payload.template_name,
            tone=payload.tone,
            length=payload.length,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GenerateCoverLetterResponse(**result)


@router.get("/history", response_model=CoverLetterHistoryResponse)
def get_cover_letter_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoverLetterHistoryResponse:
    service = CoverLetterGeneratorService(db)
    data = service.history(current_user, page, size)
    return CoverLetterHistoryResponse(
        items=[CoverLetterHistoryItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        size=data["size"],
    )


@router.get("/{letter_id}", response_model=CoverLetterDetail)
def get_cover_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoverLetterDetail:
    service = CoverLetterGeneratorService(db)
    item = service.get_by_id(current_user, letter_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover letter not found")
    return CoverLetterDetail.model_validate(item)


@router.put("/{letter_id}", response_model=CoverLetterDetail)
def update_cover_letter(
    letter_id: int,
    payload: CoverLetterUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CoverLetterDetail:
    service = CoverLetterGeneratorService(db)
    try:
        item = service.update(current_user, letter_id, payload.generated_letter)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return CoverLetterDetail.model_validate(item)


@router.delete("/{letter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = CoverLetterGeneratorService(db)
    try:
        service.delete(current_user, letter_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{letter_id}/download")
def download_cover_letter(
    letter_id: int,
    format: str = Query(default="pdf"),  # noqa: A002
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = CoverLetterGeneratorService(db)
    try:
        if format.lower() == "docx":
            content, content_type, filename = service.download_docx(current_user, letter_id)
        else:
            content, content_type, filename = service.download_pdf(current_user, letter_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
