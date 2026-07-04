# AI Job Application Assistant

Full-stack AI-powered job application platform with live job search, saved jobs, browser-assisted applications, resume tailoring, cover letters, recruitment monitoring, and AI interview preparation.

## Milestone 21 – Live Job Search, Browser Automation & Final Platform Integration

### Workflow
1. **Live Job Search** – Search with keyword, location, company, salary, experience, work mode, and date filters (`POST /api/v1/job-search/search`)
2. **Save Jobs** – Bookmark interesting roles (`POST /api/v1/saved-jobs`)
3. **Browser Application** – Start automated apply flow (`POST /api/v1/browser-application/start`)
4. **Review & Submit** – Confirm submission (`POST /api/v1/browser-application/{id}/submit`)
5. **Track History** – View automation runs on dashboard and Application History page

### Architecture
- **Backend models**: `LiveJobSearch`, `SavedJob`, `BrowserAutomationRecord`
- **Services**: `job_search_service.py`, `saved_job_service.py`, `browser_application_service.py` (reuses `app/services/browser/`)
- **API**: `/job-search`, `/saved-jobs`, `/browser-application`
- **Frontend**: `frontend/src/pages/job-search/`, components in `frontend/src/components/job-search/`
- **Dashboard**: applications today/week, saved jobs count, automation success rate, recent applications & saved jobs

### Pages
| Route | Page |
|-------|------|
| `/job-search` | Live job search with advanced filters |
| `/saved-jobs` | Saved job bookmarks |
| `/browser-application` | Start browser-assisted apply |
| `/application-history` | Automation history table |

### Testing
```bash
python -m pytest backend/app/tests/
cd frontend && npm test && npm run build
```

## Milestone 17 – AI Interview Preparation System

### Workflow
1. Generate interview preparation from a job (`POST /api/v1/interviews/generate/{job_id}`)
2. Poll preparation status until `completed`
3. Review readiness score, topics, and question categories
4. Start a mock practice session (`POST /api/v1/interviews/{id}/start`)
5. Submit answers one at a time (`POST /api/v1/interviews/{id}/answer`)
6. Finish session and view AI feedback (`POST /api/v1/interviews/{id}/finish`, `GET /api/v1/interviews/{id}/feedback`)

### Architecture
- **Backend models**: `InterviewPreparation`, `InterviewQuestion`, `InterviewAnswer`, `InterviewFeedback`, `InterviewSession`
- **Service**: `backend/app/services/interview_service.py` (generation, caching, scoring, sessions)
- **API**: `backend/app/api/v1/endpoints/interviews.py`
- **Frontend**: pages under `frontend/src/pages/interviews/`, hooks `useInterviews`, service `interviews.service.ts`
- **Dashboard**: recent practice sessions, readiness averages, weakest/strongest topics

### Testing
```bash
python -m pytest backend/app/tests/test_interviews.py
cd frontend && npm test && npm run build
```

## Structure Overview
- backend/: FastAPI application, domain services, and database layer
- frontend/: React + Vite client application
- ai/: AI orchestration, prompts, and integrations
- automation/: Playwright/browser automation scripts
- database/: Database migrations and seed data
- reports/: Analytics and export outputs
- uploads/: Resume and cover letter storage
- documents/: Architecture, API, and guide documentation
- tests/: Unit, integration, and end-to-end tests
