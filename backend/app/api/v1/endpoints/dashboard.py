from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.dashboard import (
    AggregationHistoryResponse,
    AggregationStatsResponse,
    ClosingSoonResponse,
    DashboardJobListResponse,
    DashboardResponse,
    DashboardStatistics,
    DashboardWalkInListResponse,
    JobsByCityResponse,
    NotificationCandidatesResponse,
    RecentCompaniesResponse,
    RefreshResponse,
)
from app.services.dashboard.aggregation_service import AggregationService
from app.services.dashboard.cache import DashboardCache
from app.services.dashboard.dashboard_service import DashboardService
from app.services.dashboard.notification_prep_service import NotificationPrepService
from app.services.jobs.duplicate_detection_service import DuplicateDetectionService
from app.services.jobs.parser_service import JobParserService
from app.services.jobs.providers.sample_provider import SampleJobProvider
from app.services.jobs.providers.walkin_provider import SampleWalkInProvider
from app.services.jobs.search_service import JobSearchService
from app.services.jobs.walk_in_duplicate_detection_service import WalkInDuplicateDetectionService
from app.services.jobs.walk_in_parser_service import WalkInParserService
from app.services.jobs.walk_in_service import WalkInEventService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_dashboard_cache = DashboardCache(ttl_seconds=settings.dashboard_cache_ttl_seconds)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db=db, cache=_dashboard_cache)


def get_aggregation_service(db: Session = Depends(get_db)) -> AggregationService:
    job_providers = [SampleJobProvider()]
    walk_in_providers = [SampleWalkInProvider()]
    return AggregationService(
        db=db,
        job_providers=job_providers,
        walk_in_providers=walk_in_providers,
        job_service=JobSearchService(
            db=db,
            providers=job_providers,
            parser=JobParserService(),
            duplicate_detector=DuplicateDetectionService(),
        ),
        walk_in_service=WalkInEventService(
            db=db,
            providers=walk_in_providers,
            parser=WalkInParserService(),
            duplicate_detector=WalkInDuplicateDetectionService(),
        ),
    )


def get_notification_service(db: Session = Depends(get_db)) -> NotificationPrepService:
    return NotificationPrepService(db=db)


@router.get("", response_model=DashboardResponse, summary="Get full personalized dashboard")
def get_dashboard(
    request: Request,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardResponse:
    payload = service.get_full_dashboard(user, page=page, size=size)
    manager = getattr(request.app.state, "browser_manager", None)
    if manager is not None and "statistics" in payload:
        payload["statistics"].update(manager.form_stats_summary())
    return payload


@router.get("/new-jobs", response_model=DashboardJobListResponse, summary="Get new jobs for the user")
def get_new_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_new_jobs(user, page=page, size=size)


@router.get("/recommended", response_model=DashboardJobListResponse, summary="Get recommended jobs")
def get_recommended_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_recommended_jobs(user, page=page, size=size)


@router.get("/high-matches", response_model=DashboardJobListResponse, summary="Get high match jobs (90%+)")
def get_high_matches(
    min_score: int = Query(default=90, ge=0, le=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_high_match_jobs(user, min_score=min_score, page=page, size=size)


@router.get("/walk-ins", response_model=DashboardWalkInListResponse, summary="Get personalized walk-in drives")
def get_walk_ins(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardWalkInListResponse:
    return service.get_walk_ins(user, page=page, size=size)


@router.get("/walk-ins/today", response_model=DashboardWalkInListResponse, summary="Get today's walk-in drives")
def get_todays_walk_ins(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardWalkInListResponse:
    return service.get_todays_walk_ins(user, page=page, size=size)


@router.get("/walk-ins/upcoming", response_model=DashboardWalkInListResponse, summary="Get upcoming walk-in drives")
def get_upcoming_walk_ins(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardWalkInListResponse:
    return service.get_upcoming_walk_ins(user, page=page, size=size)


@router.get("/closing-soon", response_model=ClosingSoonResponse, summary="Get jobs and walk-ins closing soon")
def get_closing_soon(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> ClosingSoonResponse:
    return service.get_closing_soon(user, page=page, size=size)


@router.get("/remote", response_model=DashboardJobListResponse, summary="Get remote jobs")
def get_remote_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_remote_jobs(user, page=page, size=size)


@router.get("/hybrid", response_model=DashboardJobListResponse, summary="Get hybrid jobs")
def get_hybrid_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_hybrid_jobs(user, page=page, size=size)


@router.get("/jobs-by-city", response_model=JobsByCityResponse, summary="Get job counts by city")
def get_jobs_by_city(
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> JobsByCityResponse:
    return service.get_jobs_by_city(user)


@router.get("/recent-companies", response_model=RecentCompaniesResponse, summary="Get recently added companies")
def get_recent_companies(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> RecentCompaniesResponse:
    return service.get_recent_companies(user, page=page, size=size)


@router.get("/recently-updated", response_model=DashboardJobListResponse, summary="Get recently updated jobs")
def get_recently_updated_jobs(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardJobListResponse:
    return service.get_recently_updated_jobs(user, page=page, size=size)


@router.get("/statistics", response_model=DashboardStatistics, summary="Get dashboard statistics")
def get_statistics(
    request: Request,
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardStatistics:
    stats = service.get_statistics(user)
    manager = getattr(request.app.state, "browser_manager", None)
    if manager is not None:
        stats.update(manager.form_stats_summary())
    return stats


@router.get("/notification-candidates", response_model=NotificationCandidatesResponse, summary="Get notification candidates (prep only)")
def get_notification_candidates(
    user: User = Depends(get_current_active_user),
    service: NotificationPrepService = Depends(get_notification_service),
) -> NotificationCandidatesResponse:
    return service.identify_candidates(user)


@router.post("/refresh", response_model=RefreshResponse, summary="Refresh user dashboard matches")
def refresh_dashboard(
    user: User = Depends(get_current_active_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> RefreshResponse:
    return service.refresh_user_feed(user)


@router.post("/aggregate", response_model=AggregationStatsResponse, summary="Manually trigger full aggregation")
def trigger_aggregation(
    user: User = Depends(get_current_active_user),
    aggregation: AggregationService = Depends(get_aggregation_service),
) -> AggregationStatsResponse:
    try:
        return aggregation.run_full_aggregation()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/aggregation/history", response_model=AggregationHistoryResponse, summary="Get aggregation run history")
def get_aggregation_history(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_active_user),
    aggregation: AggregationService = Depends(get_aggregation_service),
) -> AggregationHistoryResponse:
    return aggregation.get_aggregation_history(page=page, size=size)
