from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, jobs, profile, resumes

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(resumes.router)
router.include_router(jobs.router)
