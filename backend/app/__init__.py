from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.services.dashboard.cache import DashboardCache
from app.services.browser.browser_manager import BrowserManager
from app.services.jobs.scheduler import AggregationScheduler, WalkInScheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database resources when the application starts."""
    init_db()

    dashboard_cache = DashboardCache(ttl_seconds=settings.dashboard_cache_ttl_seconds)
    app.state.dashboard_cache = dashboard_cache
    browser_manager = BrowserManager()
    browser_manager.start()
    app.state.browser_manager = browser_manager

    walk_in_scheduler: WalkInScheduler | None = None
    aggregation_scheduler: AggregationScheduler | None = None

    if settings.walk_in_scheduler_enabled and not settings.aggregation_scheduler_enabled:
        walk_in_scheduler = WalkInScheduler()
        walk_in_scheduler.start()
        walk_in_scheduler.add_refresh_job(
            job_id="walk-in-refresh",
            interval_minutes=settings.walk_in_refresh_interval_minutes,
        )

    if settings.aggregation_scheduler_enabled:
        aggregation_scheduler = AggregationScheduler(on_dashboard_refresh=dashboard_cache.clear)
        aggregation_scheduler.start()
        aggregation_scheduler.add_full_aggregation(
            job_id="full-aggregation",
            interval_minutes=min(settings.job_refresh_interval_minutes, settings.walk_in_refresh_interval_minutes),
        )
        if settings.job_scheduler_enabled:
            aggregation_scheduler.add_job_aggregation(
                job_id="job-aggregation",
                interval_minutes=settings.job_refresh_interval_minutes,
            )
        aggregation_scheduler.add_walk_in_refresh(
            job_id="walk-in-refresh",
            interval_minutes=settings.walk_in_refresh_interval_minutes,
        )
        aggregation_scheduler.add_dashboard_refresh(
            job_id="dashboard-cache-refresh",
            interval_minutes=settings.dashboard_refresh_interval_minutes,
        )
    elif settings.job_scheduler_enabled:
        aggregation_scheduler = AggregationScheduler()
        aggregation_scheduler.start()
        aggregation_scheduler.add_job_aggregation(
            job_id="job-aggregation",
            interval_minutes=settings.job_refresh_interval_minutes,
        )

    app.state.walk_in_scheduler = walk_in_scheduler
    app.state.aggregation_scheduler = aggregation_scheduler
    yield

    if walk_in_scheduler is not None:
        walk_in_scheduler.shutdown()
    if aggregation_scheduler is not None:
        aggregation_scheduler.shutdown()
    browser_manager.shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(api_v1_router)
    return app


app = create_app()
