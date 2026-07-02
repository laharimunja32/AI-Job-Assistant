# AI Job Application Assistant

This project scaffold provides a production-ready directory structure for a full-stack AI-powered job application platform.

## Structure Overview

- `backend/`: FastAPI application, domain services, and database layer
- `frontend/`: React + Vite client application
- `ai/`: AI orchestration, prompts, and integrations
- `automation/`: Playwright/browser automation scripts
- `database/`: Database migrations and seed data
- `reports/`: Analytics and export outputs
- `uploads/`: Resume and cover letter storage
- `documents/`: Architecture, API, and guide documentation
- `tests/`: Unit, integration, and end-to-end tests

## Current Capabilities

- Authentication and user management
- User profile and resume management
- Job search engine with provider-based discovery
- AI job matcher (profile/resume scoring against jobs)
- **Walk-in drive discovery** (Milestone 6.1)
- **Automatic job aggregation & smart dashboard** (Milestone 7)
- **Production-ready React frontend** (Milestone 8)
- **AI resume tailoring engine** with ATS score, history, multi-format download, and dashboard insights (Milestone 9)
- **AI cover letter generation engine** with queueing, caching, version history, templates, and multi-format output (Milestone 10)
- **Browser automation foundation** with Playwright session lifecycle, navigation APIs, and dashboard/browser UI integration (Milestone 12)
- **Intelligent form detection and profile-based auto-fill** with field confidence, manual input reporting, and dashboard fill metrics (Milestone 13)
- **Intelligent resume and cover-letter upload automation** with secure document ownership checks, upload status tracking, and dashboard upload analytics (Milestone 14)
- **Guided review and assisted submission workflow** with explicit confirmation, validation/audit history, review readiness scoring, and review-centric dashboard metrics (Milestone 15)
- **Email & assessment monitoring** with authorized email processing, interview/assessment/reminder tracking, unified timeline, notification history, and dashboard deadline insights (Milestone 16)

## Frontend (Milestone 8)

The `frontend/` directory contains a complete React 19 + TypeScript client:

- Personalized dashboard loads automatically after login — no search required
- Jobs, walk-ins, resumes, profile, notifications, and settings
- JWT auth with refresh token handling and protected routes
- TanStack Query for API state, Zustand for auth/UI/bookmarks

See [frontend/README.md](frontend/README.md) for full documentation.

## Automatic Job Feed & Smart Dashboard (Milestone 7)

The backend now transforms from search-based to feed-based job discovery:

- **AggregationService** collects jobs and walk-ins from all configured providers on a schedule
- **DashboardService** serves a personalized job feed using profile, resume, and AI match scores — no manual search required
- REST API under `/api/v1/dashboard` with sections for new jobs, high matches, recommendations, walk-ins, remote/hybrid jobs, closing soon, and more
- **NotificationPrepService** identifies future notification candidates without sending them yet
- Configurable scheduler via `AGGREGATION_SCHEDULER_ENABLED`, `JOB_REFRESH_INTERVAL_MINUTES`, `WALKIN_REFRESH_INTERVAL_MINUTES`, `DASHBOARD_REFRESH_INTERVAL_MINUTES`

See [backend/README.md](backend/README.md) for full API documentation and architecture.

## AI Resume Tailoring (Milestone 9)

Milestone 9 adds a complete tailored-resume workflow integrated with the existing job detail button and dashboard:

- Backend data models and API: `backend/app/db/models/resume_tailoring.py`, `backend/app/api/v1/endpoints/resume_tailoring.py`, `backend/app/schemas/resume_tailoring.py`
- Backend orchestration: `backend/app/services/resume_tailoring_service.py` (analysis extraction, ATS scoring, queue execution, caching, versioning, multi-format outputs)
- Dashboard integration: `backend/app/services/dashboard/dashboard_service.py`, `backend/app/schemas/dashboard.py`
- Frontend generation flow: `frontend/src/pages/jobs/JobDetailPage.tsx`, `frontend/src/services/resumeTailoring.service.ts`, `frontend/src/hooks/useResumeTailoring.ts`
- Frontend dashboard sections: `frontend/src/pages/dashboard/DashboardPage.tsx`
- Shared frontend contracts: `frontend/src/types/api.ts`
- Tests: `backend/app/tests/test_resume_tailoring.py`, `frontend/src/test/hooks/useResumeTailoring.test.tsx`

## AI Cover Letter Generation (Milestone 10)

Milestone 10 delivers a full cover-letter pipeline integrated with jobs, resumes, AI match analysis, and dashboard insights:

- Backend data models and API: `backend/app/db/models/cover_letter.py`, `backend/app/api/v1/endpoints/cover_letters.py`, `backend/app/schemas/cover_letter.py`
- Backend orchestration: `backend/app/services/cover_letter_service.py` (analysis extraction, queue + retries, duplicate caching, versioning, and output generation)
- Dashboard integration: `backend/app/services/dashboard/dashboard_service.py`, `backend/app/schemas/dashboard.py`
- Frontend generation flow and reusable UI: `frontend/src/pages/jobs/JobDetailPage.tsx`, `frontend/src/components/cover-letters/*`
- Frontend API integration: `frontend/src/services/coverLetters.service.ts`, `frontend/src/hooks/useCoverLetters.ts`, `frontend/src/types/api.ts`
- Application selection integration: `frontend/src/pages/applications/ApplicationsPage.tsx`, `frontend/src/store/applicationsStore.ts`
- Tests: `backend/app/tests/test_cover_letters.py`, `frontend/src/test/hooks/useCoverLetters.test.tsx`

## Application Management System (Milestone 11)

Milestone 11 adds a centralized application workflow layer that persists every application and linked documents, while intentionally avoiding browser automation:

- Backend models and APIs: `backend/app/db/models/application.py`, `backend/app/schemas/application.py`, `backend/app/services/application_service.py`, `backend/app/api/v1/endpoints/applications.py`
- Dashboard integration: application-centric counters are now included in `GET /api/v1/dashboard/statistics`
- Frontend application center: `frontend/src/pages/applications/ApplicationsPage.tsx`
- Job detail preparation flow: `frontend/src/pages/jobs/JobDetailPage.tsx` now supports document selection + **Prepare Application** (`ready_to_apply`)
- Frontend integration layer: `frontend/src/services/applications.service.ts`, `frontend/src/hooks/useApplications.ts`, `frontend/src/types/api.ts`
- Tests: `backend/app/tests/test_applications.py`, `frontend/src/test/hooks/useApplications.test.tsx`

Explicitly out of scope in this milestone:

- Browser automation
- Form filling/upload automation
- CAPTCHA handling
- Auto submission

## Browser Automation Foundation (Milestone 12)

Milestone 12 introduces a reusable Playwright-powered browser layer that opens application pages and manages resilient browser sessions for future automation modules:

- Backend browser infrastructure: `backend/app/services/browser/browser_manager.py`, `backend/app/services/browser/navigation_service.py`
- Backend persistence + APIs: `backend/app/db/models/browser_session.py`, `backend/app/schemas/browser.py`, `backend/app/api/v1/endpoints/browser.py`
- App lifecycle integration: `backend/app/__init__.py` initializes and shuts down the browser manager
- Frontend browser console: `frontend/src/pages/browser/BrowserAutomationPage.tsx`
- Dashboard widget integration: browser health/activity metrics in `GET /api/v1/dashboard/statistics`
- Tests: `backend/app/tests/test_browser_automation.py`, `frontend/src/test/hooks/useBrowserAutomation.test.tsx`, `frontend/src/test/components/BrowserAutomationPage.test.tsx`

This milestone intentionally excludes form detection/filling, uploads, CAPTCHA handling, and auto-submit.

## Intelligent Form Detection & Auto-Fill (Milestone 13)

Milestone 13 extends browser automation with safe, profile-driven form assistance:

- Backend detection engine classifies common job fields using labels, placeholders, `name`, aria labels, and nearby text.
- Auto-fill service maps fields to authenticated user data from profile, active resume metadata, contact details, and preferences.
- New APIs:
  - `POST /api/v1/browser/forms/detect/{session_id}`
  - `POST /api/v1/browser/forms/fill/{session_id}`
  - `GET /api/v1/browser/forms/report/{session_id}`
- Frontend adds a dedicated `/form-assistant` page to:
  - review detected fields and confidence
  - edit override values before fill
  - view completion %, missing fields, and required manual inputs
- Dashboard browser section now surfaces form automation metrics:
  - forms detected
  - fields filled
  - manual fields remaining
  - average fill success rate

Intentional exclusions for this milestone:

- Resume upload automation
- Cover-letter upload automation
- CAPTCHA solving
- Auto-submit
- Email monitoring

## Intelligent Upload Automation (Milestone 14)

Milestone 14 extends browser automation with upload-specific intelligence while keeping final submission explicitly out of scope:

- Backend upload services:
  - `UploadDetectionService` for file-input, hidden-input, button-triggered, and drag/drop-capable target detection
  - `DocumentUploadService` for resume/tailored-resume/cover-letter selection and controlled upload execution
  - `UploadValidationService` for file type checks, size checks, completion verification, and retry-ready validation signals
- New upload APIs:
  - `POST /api/v1/browser/uploads/detect/{session_id}`
  - `POST /api/v1/browser/uploads/resume/{session_id}`
  - `POST /api/v1/browser/uploads/cover-letter/{session_id}`
  - `POST /api/v1/browser/uploads/all/{session_id}`
  - `GET /api/v1/browser/uploads/status/{session_id}`
  - `POST /api/v1/browser/uploads/retry/{session_id}`
- Frontend upload assistant:
  - `/upload-assistant` page for field detection, document selection visibility, upload progress, status, validation outcomes, and retries
- Dashboard metrics now include:
  - successful uploads
  - failed uploads
  - resume upload count
  - cover-letter upload count
  - average upload time

Security guardrails in this milestone:

- Uploads only use application-managed documents.
- Selected resume/tailored resume/cover letter ownership is validated against the authenticated user.
- Arbitrary local path uploads are not allowed.

## Guided Review & Assisted Submission (Milestone 15)

Milestone 15 adds a reliable pre-submit review workflow while keeping CAPTCHA/anti-bot bypass out of scope:

- Backend review architecture:
  - `ReviewService` analyzes current browser automation state and returns filled fields, missing required fields, uploaded docs, warnings/errors, and readiness score.
  - `SubmissionValidationService` validates required fields/doc uploads/session state and returns structured checks.
  - `SubmissionAuditService` records end-to-end review/submission audit trail and updates application status/history.
- New browser review APIs:
  - `GET /api/v1/browser/review/{session_id}`
  - `POST /api/v1/browser/review/validate/{session_id}`
  - `POST /api/v1/browser/review/confirm/{session_id}`
  - `GET /api/v1/browser/review/history/{application_id}`
- Frontend guided review center:
  - `/review-assistant` page for review summary, editable overrides, validation refresh, rerun actions, explicit confirmation dialog, and submission-history visibility.
- Application lifecycle and dashboard updates:
  - New review-oriented statuses: `ready_to_submit`, `review_required`, `submitted`, `submission_failed`
  - Dashboard statistics now include: ready-to-submit, under-review, submitted-today, validation-failures, and average-readiness-score.

Out of scope remains unchanged:

- CAPTCHA solving
- Anti-bot bypassing
- Email monitoring
- Interview scheduling

## Walk-in Drive Search (Milestone 6.1)

The backend extends the job search engine with a dedicated walk-in provider pipeline:

- `WalkInEvent` database model for walk-in-specific fields (venue, walk-in date/time, eligibility, documents, etc.)
- Provider-based architecture (`WalkInProvider`) for adding new walk-in sources
- REST API under `/api/v1/walk-ins` for listing, filtering, and refreshing walk-in data
- Automatic sync into the shared `jobs` table so walk-in drives work with the existing AI Job Matcher
- Scheduler support for periodic walk-in refresh (`WALK_IN_SCHEDULER_ENABLED=true`)

See [backend/README.md](backend/README.md) and [backend/app/services/jobs/README.md](backend/app/services/jobs/README.md) for file-level documentation.

## Getting Started

1. Configure environment variables in `backend/.env` (see `backend/app/core/config.py`).
2. Start the backend API from the `backend` directory.
3. Start the frontend from the `frontend` directory (`npm install && npm run dev`).
4. Open `http://localhost:5173` and register or log in.
