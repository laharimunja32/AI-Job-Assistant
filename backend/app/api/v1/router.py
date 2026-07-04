from fastapi import APIRouter

from app.api.v1.endpoints import (
    applications,
    auth,
    browser,
    browser_application,
    cover_letter_generator,
    cover_letters,
    dashboard,
    health,
    interview_feedback,
    interviews,
    job_search,
    jobs,
    matches,
    profile,
    recruitment_monitoring,
    resume_optimizer,
    resume_tailoring,
    resumes,
    saved_jobs,
    walk_ins,
)

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(resumes.router)
router.include_router(jobs.router)
router.include_router(matches.router)
router.include_router(walk_ins.router)
router.include_router(dashboard.router)
router.include_router(resume_tailoring.router)
router.include_router(resume_optimizer.router)
router.include_router(cover_letter_generator.router)
router.include_router(cover_letters.router)
router.include_router(applications.router)
router.include_router(browser.router)
router.include_router(job_search.router)
router.include_router(saved_jobs.router)
router.include_router(browser_application.router)
router.include_router(recruitment_monitoring.router)
router.include_router(interviews.router)
router.include_router(interview_feedback.router)
