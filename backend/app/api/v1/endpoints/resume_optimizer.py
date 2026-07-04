from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.resume_optimizer import (
    ResumeOptimizationHistoryResponse,
    ResumeOptimizationHistoryItem,
    ResumeOptimizationRead,
    ResumeOptimizerAnalyzeRequest,
    ResumeOptimizerAnalyzeResponse,
)
from app.services.resume_optimizer_service import ResumeOptimizerService

router = APIRouter(prefix="/resume-optimizer", tags=["resume-optimizer"])


@router.post("/analyze", response_model=ResumeOptimizerAnalyzeResponse)
def analyze_resume(
    payload: ResumeOptimizerAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeOptimizerAnalyzeResponse:
    service = ResumeOptimizerService(db)
    try:
        result = service.analyze(
            current_user,
            payload.resume_id,
            payload.job_description,
            job_title=payload.job_title,
            company_name=payload.company_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ResumeOptimizerAnalyzeResponse(**result)


@router.get("/history", response_model=ResumeOptimizationHistoryResponse)
def get_optimization_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeOptimizationHistoryResponse:
    service = ResumeOptimizerService(db)
    data = service.get_history(current_user, page, size)
    return ResumeOptimizationHistoryResponse(
        items=[ResumeOptimizationHistoryItem.model_validate(item) for item in data["items"]],
        total=data["total"],
        page=data["page"],
        size=data["size"],
    )


@router.get("/{analysis_id}", response_model=ResumeOptimizationRead)
def get_optimization_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ResumeOptimizationRead:
    service = ResumeOptimizerService(db)
    item = service.get_analysis(current_user, analysis_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return ResumeOptimizationRead(**service._to_read_response(item))


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_optimization_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = ResumeOptimizerService(db)
    try:
        service.delete_analysis(current_user, analysis_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{analysis_id}/download")
def download_optimized_resume(
    analysis_id: int,
    format: str = Query(default="pdf"),  # noqa: A002
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    service = ResumeOptimizerService(db)
    try:
        content, content_type, filename = service.download(current_user, analysis_id, format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(content=content, media_type=content_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
