from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.session import get_db
from app.schemas.job import JobCreateUpdate, JobListResponse, JobRead
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.sample_provider import SampleJobProvider
from app.services.jobs.search_service import JobSearchService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_search_service(db: Session = Depends(get_db)) -> JobSearchService:
    return JobSearchService(
        db=db,
        providers=[SampleJobProvider()],
        parser=JobParserService(),
        duplicate_detector=DuplicateDetectionService(),
    )


@router.get("", response_model=JobListResponse, summary="Search and list jobs")
def search_jobs(
    keyword: str | None = Query(default=None),
    location: str | None = Query(default=None),
    work_mode: str | None = Query(default=None),
    employment_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: JobSearchService = Depends(get_search_service),
) -> JobListResponse:
    filters = {k: v for k, v in {"work_mode": work_mode, "employment_type": employment_type}.items() if v is not None}
    return service.search_jobs(keyword=keyword, location=location, filters=filters, page=page, size=size)


@router.get("/all", response_model=JobListResponse, summary="List persisted jobs")
def list_jobs(
    keyword: str | None = Query(default=None),
    location: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: JobSearchService = Depends(get_search_service),
) -> JobListResponse:
    return service.list_jobs(keyword=keyword, location=location, page=page, size=size)


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED, summary="Save a job")
def save_job(payload: JobCreateUpdate, service: JobSearchService = Depends(get_search_service)) -> JobRead:
    return service.save_job(payload.model_dump())


@router.put("/{job_id}", response_model=JobRead, summary="Update a job")
def update_job(job_id: int, payload: JobCreateUpdate, service: JobSearchService = Depends(get_search_service)) -> JobRead:
    try:
        return service.update_job(job_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a job")
def delete_job(job_id: int, service: JobSearchService = Depends(get_search_service)) -> Response:
    job = service.db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    service.db.delete(job)
    service.db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
