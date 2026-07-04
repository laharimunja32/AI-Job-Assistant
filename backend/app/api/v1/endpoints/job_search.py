from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.job_search import (
    JobSearchDetailResponse,
    JobSearchHistoryResponse,
    JobSearchHistoryItem,
    JobSearchRequest,
    JobSearchResponse,
    LiveJobResult,
)
from app.services.job_search_service import LiveJobSearchService
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.sample_provider import SampleJobProvider

router = APIRouter(prefix="/job-search", tags=["job-search"])


def get_live_job_search_service(db: Session = Depends(get_db)) -> LiveJobSearchService:
    return LiveJobSearchService(
        db=db,
        providers=[SampleJobProvider()],
        parser=JobParserService(),
        duplicate_detector=DuplicateDetectionService(),
    )


@router.post("/search", response_model=JobSearchResponse, summary="Live job search with advanced filters")
def search_jobs(
    payload: JobSearchRequest,
    current_user: User = Depends(get_current_active_user),
    service: LiveJobSearchService = Depends(get_live_job_search_service),
) -> JobSearchResponse:
    result = service.search(current_user.id, payload)
    return JobSearchResponse(
        items=[LiveJobResult(**item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
    )


@router.get("/history", response_model=JobSearchHistoryResponse, summary="Get job search history")
def get_search_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: LiveJobSearchService = Depends(get_live_job_search_service),
) -> JobSearchHistoryResponse:
    result = service.get_history(current_user.id, limit=limit)
    return JobSearchHistoryResponse(
        items=[JobSearchHistoryItem.model_validate(item) for item in result["items"]],
        total=result["total"],
    )


@router.get("/{search_id}", response_model=JobSearchDetailResponse, summary="Get job search details")
def get_search_detail(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    service: LiveJobSearchService = Depends(get_live_job_search_service),
) -> JobSearchDetailResponse:
    record = service.get_search_by_id(current_user.id, search_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search record not found")
    return JobSearchDetailResponse.model_validate(record)
