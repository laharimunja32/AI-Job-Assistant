from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database resources when the application starts."""
    init_db()
    try:
        from app.services.browser.browser_manager import BrowserManager

        app.state.browser_manager = BrowserManager()
    except Exception:
        app.state.browser_manager = None
    yield
    manager = getattr(app.state, "browser_manager", None)
    if manager is not None:
        try:
            manager.shutdown()
        except Exception:
            pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(api_v1_router)

    @app.get("/", tags=["root"], summary="API root")
    def root() -> dict[str, str]:
        """Return a quick API status payload for browser checks."""
        return {"service": settings.app_name, "status": "running", "docs": "/docs"}

    return app


app = create_app()
