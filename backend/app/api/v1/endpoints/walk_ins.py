from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.walk_in import WalkInListResponse, WalkInRefreshResponse
from app.services.jobs.providers.walkin_provider import SampleWalkInProvider
from app.services.jobs.walk_in_duplicate_detection_service import WalkInDuplicateDetectionService
from app.services.jobs.walk_in_parser_service import WalkInParserService
from app.services.jobs.walk_in_service import WalkInEventService

router = APIRouter(prefix="/walk-ins", tags=["walk-ins"])


def get_walk_in_service(db: Session = Depends(get_db)) -> WalkInEventService:
    return WalkInEventService(
        db=db,
        providers=[SampleWalkInProvider()],
        parser=WalkInParserService(),
        duplicate_detector=WalkInDuplicateDetectionService(),
    )


@router.get("", response_model=WalkInListResponse, summary="List all walk-in drives")
def list_walk_ins(
    company: str | None = Query(default=None, description="Filter by company name"),
    role: str | None = Query(default=None, description="Filter by job role"),
    city: str | None = Query(default=None, description="Filter by city"),
    eligibility: str | None = Query(default=None, description="Filter by eligibility"),
    walk_in_date: date | None = Query(default=None, description="Filter by walk-in date"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: WalkInEventService = Depends(get_walk_in_service),
) -> WalkInListResponse:
    return service.search_walk_ins(
        company=company,
        role=role,
        city=city,
        eligibility=eligibility,
        walk_in_date=walk_in_date,
        page=page,
        size=size,
    )


@router.get("/today", response_model=WalkInListResponse, summary="List today's walk-in drives")
def get_todays_walk_ins(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: WalkInEventService = Depends(get_walk_in_service),
) -> WalkInListResponse:
    return service.get_todays_walk_ins(page=page, size=size)


@router.get("/upcoming", response_model=WalkInListResponse, summary="List upcoming walk-in drives")
def get_upcoming_walk_ins(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: WalkInEventService = Depends(get_walk_in_service),
) -> WalkInListResponse:
    return service.get_upcoming_walk_ins(page=page, size=size)


@router.post("/refresh", response_model=WalkInRefreshResponse, summary="Refresh walk-in data from providers")
def refresh_walk_ins(
    keyword: str | None = Query(default=None),
    location: str | None = Query(default=None),
    eligibility: str | None = Query(default=None),
    service: WalkInEventService = Depends(get_walk_in_service),
) -> WalkInRefreshResponse:
    filters = {"eligibility": eligibility} if eligibility else None
    return service.refresh_walk_ins(keyword=keyword, location=location, filters=filters)
