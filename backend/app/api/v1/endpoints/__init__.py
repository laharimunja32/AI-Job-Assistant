from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.browser import router as browser_router
from app.api.v1.endpoints.cover_letters import router as cover_letters_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.recruitment_monitoring import router as recruitment_monitoring_router
from app.api.v1.endpoints.resume_tailoring import router as resume_tailoring_router
from app.api.v1.endpoints.resumes import router as resumes_router

__all__ = [
    "applications_router",
    "auth_router",
    "browser_router",
    "cover_letters_router",
    "health_router",
    "profile_router",
    "recruitment_monitoring_router",
    "resume_tailoring_router",
    "resumes_router",
]
