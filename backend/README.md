# Backend

This module contains the FastAPI backend for the AI Job Assistant.

## Milestone 16 – Email & Assessment Monitoring

### Added modules

- `app/db/models/recruitment_monitoring.py`: `EmailEvent`, `Assessment`, `Interview`, `TimelineEvent`, `Reminder`, `NotificationHistory`.
- `app/services/recruitment_monitoring_service.py`: authorized email processing, extraction, application association, timeline/reminder/notification orchestration.
- `app/schemas/recruitment_monitoring.py`: API contracts for emails, assessments, interviews, timeline, reminders, notification history.
- `app/api/v1/endpoints/recruitment_monitoring.py`: new `/api/v1/*` monitoring endpoints.
- `app/tests/test_recruitment_monitoring.py`: authorization guard + core flow coverage.

### New API endpoints

- `GET /api/v1/emails`
- `GET /api/v1/emails/{id}`
- `POST /api/v1/emails/process` (requires `authorization_confirmed=true`)
- `GET /api/v1/assessments`
- `POST /api/v1/assessments`
- `PUT /api/v1/assessments/{id}`
- `GET /api/v1/interviews`
- `POST /api/v1/interviews`
- `PUT /api/v1/interviews/{id}`
- `GET /api/v1/timeline/{application_id}`
- `POST /api/v1/reminders`
- `GET /api/v1/reminders`
- `PUT /api/v1/reminders/{id}`
- `DELETE /api/v1/reminders/{id}`
- `GET /api/v1/notifications/history`

### Security and integration approach

- Email integration is explicitly authorization-gated; requests without authorization are rejected.
- No email password storage, mailbox scraping, or provider login automation is implemented.
- Processing flow is designed for official provider API payloads and user-provided content.

## Milestone 15 – Guided Review & Assisted Submission

### Created files

- [app/db/models/submission_review.py](app/db/models/submission_review.py): `SubmissionReviewAudit` model for review/submission audit timeline.
- [app/services/browser/review_service.py](app/services/browser/review_service.py): Page/application review analysis + readiness score generation.
- [app/services/browser/submission_validation_service.py](app/services/browser/submission_validation_service.py): Structured submission validation checks.
- [app/services/browser/submission_audit_service.py](app/services/browser/submission_audit_service.py): Persists audits and updates application status/history after explicit confirmation.

### Updated files

- [app/api/v1/endpoints/browser.py](app/api/v1/endpoints/browser.py): Adds guided review, validation, confirmation, and review history endpoints.
- [app/schemas/browser.py](app/schemas/browser.py): Adds review/validation/confirmation/audit response contracts.
- [app/schemas/application.py](app/schemas/application.py): Adds `ready_to_submit`, `review_required`, `submitted`, `submission_failed` statuses.
- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py) and [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds review-centric dashboard statistics.
- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Registers review audit model.
- [app/tests/test_browser_automation.py](app/tests/test_browser_automation.py): Adds guided review API coverage.

### Guided review API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/browser/review/{session_id}` | Build full guided review report for the active browser/application context |
| `POST` | `/api/v1/browser/review/validate/{session_id}` | Run structured validation checks |
| `POST` | `/api/v1/browser/review/confirm/{session_id}` | Record explicit user confirmation and optional submission attempt |
| `GET` | `/api/v1/browser/review/history/{application_id}` | Return historical review/submission audit entries |

## Milestone 13 – Intelligent Form Detection & Auto-Fill

### Created files

- [app/services/browser/form_detection_service.py](app/services/browser/form_detection_service.py): Detects common application fields from labels, placeholders, name attributes, aria labels, and nearby text.
- [app/services/browser/auto_fill_service.py](app/services/browser/auto_fill_service.py): Maps detected fields to profile/resume/preference data and fills supported values.

### Updated files

- [app/schemas/browser.py](app/schemas/browser.py): Adds form detection/fill/report schemas.
- [app/api/v1/endpoints/browser.py](app/api/v1/endpoints/browser.py): Adds form detect/fill/report endpoints.
- [app/services/browser/browser_manager.py](app/services/browser/browser_manager.py): Caches field mappings and latest fill report per session; tracks form automation stats.
- [app/api/v1/endpoints/dashboard.py](app/api/v1/endpoints/dashboard.py) and [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds form automation statistics in dashboard payloads.

### Form automation API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/browser/forms/detect/{session_id}` | Detect form fields on current page for owned browser session |
| `POST` | `/api/v1/browser/forms/fill/{session_id}` | Fill supported fields using profile/resume/preferences data and optional overrides |
| `GET` | `/api/v1/browser/forms/report/{session_id}` | Retrieve latest fill report (filled/skipped/unknown/manual-required fields) |

### Detection strategy

1. Collect form controls (`input`, `textarea`, `select`) from current page.
2. Build semantic context from `label`, `placeholder`, `name`, `aria-label`, and nearby container text.
3. Classify controls against common job field types with weighted keyword + input-type heuristics.
4. Store detected mapping in session cache for repeated page interactions.

### Auto-fill workflow

1. Load user-safe source data from authenticated account (`User`, `Profile`, active `Resume` metadata, work preferences).
2. Map field type to source value.
3. Fill supported controls; skip unsupported types; never touch passwords.
4. Return completion report:
   - Filled fields
   - Skipped fields
   - Unknown fields
   - Required manual input

### Scope limitations in this milestone

- No auto-submit
- No CAPTCHA solving
- No resume/cover-letter upload automation
- No password capture or storage

## Milestone 14 – Intelligent Resume & Cover Letter Upload Automation

### Created files

- [app/services/browser/upload_detection_service.py](app/services/browser/upload_detection_service.py): Detects upload-capable controls (standard file input, hidden input, button-triggered upload, drag/drop-capable zones) and classifies targets (resume, cover letter, supporting docs, portfolio).
- [app/services/browser/document_upload_service.py](app/services/browser/document_upload_service.py): Selects owned documents (tailored resume/active resume/selected cover letter), executes upload, verifies completion, and persists upload attempts/history.
- [app/services/browser/upload_validation_service.py](app/services/browser/upload_validation_service.py): Validates type/size/multi-upload capability and checks filename confirmation and upload verification messages.

### Updated files

- [app/db/models/browser_session.py](app/db/models/browser_session.py): Adds `BrowserUploadAttempt` upload history model.
- [app/schemas/browser.py](app/schemas/browser.py): Adds upload detection/request/status/validation contracts.
- [app/api/v1/endpoints/browser.py](app/api/v1/endpoints/browser.py): Adds upload detect/upload/status/retry endpoints with ownership checks.
- [app/services/browser/browser_manager.py](app/services/browser/browser_manager.py): Adds upload detection/report cache and upload metric aggregation.
- [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds upload statistics fields.
- [app/tests/test_browser_automation.py](app/tests/test_browser_automation.py): Adds upload detection endpoint test coverage.

### Upload automation API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/browser/uploads/detect/{session_id}` | Detect upload fields on current page for an owned browser session |
| `POST` | `/api/v1/browser/uploads/resume/{session_id}` | Upload resume/tailored resume only |
| `POST` | `/api/v1/browser/uploads/cover-letter/{session_id}` | Upload selected cover letter only |
| `POST` | `/api/v1/browser/uploads/all/{session_id}` | Upload resume + cover letter in one run |
| `GET` | `/api/v1/browser/uploads/status/{session_id}?application_id={id}` | Retrieve upload history/status for the session/application |
| `POST` | `/api/v1/browser/uploads/retry/{session_id}` | Retry failed uploads for resume and/or cover letter |

### Security model

- All upload endpoints require authentication.
- Browser session ownership is enforced per user.
- Application ownership is enforced per user.
- Selected `resume`, `tailored_resume`, and `cover_letter` records are verified to belong to the authenticated user before upload.
- Upload source paths are derived only from application-managed documents, not arbitrary client-provided file paths.

### Scope limitations in this milestone

- No final application submit
- No CAPTCHA solving
- No email or interview workflows

## Milestone 12 – Browser Automation Foundation

### Created files

- [app/db/models/browser_session.py](app/db/models/browser_session.py): Persistent browser session state with lifecycle/status/error/screenshot metadata.
- [app/schemas/browser.py](app/schemas/browser.py): API contracts for browser session lifecycle, navigation responses, and browser health summary.
- [app/services/browser/browser_manager.py](app/services/browser/browser_manager.py): Playwright browser launcher/reuse layer with session tracking, crash handling, and idle cleanup.
- [app/services/browser/navigation_service.py](app/services/browser/navigation_service.py): Apply URL navigation with timeout/redirect handling and metadata extraction.
- [app/api/v1/endpoints/browser.py](app/api/v1/endpoints/browser.py): Protected browser automation endpoints.
- [app/tests/test_browser_automation.py](app/tests/test_browser_automation.py): Browser manager/session lifecycle/security/API coverage.

### Updated files

- [app/core/config.py](app/core/config.py): Adds Playwright + session environment configuration.
- [app/__init__.py](app/__init__.py): Initializes `BrowserManager` in app lifespan and performs graceful shutdown.
- [app/api/v1/router.py](app/api/v1/router.py): Registers `/api/v1/browser` routes.
- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Registers browser session model for table creation.
- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py): Adds browser activity/success/health stats to dashboard.
- [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds browser statistic fields.
- [requirements.txt](requirements.txt): Adds Playwright dependency.

### Browser Automation API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/browser/session` | Create a browser session (`chromium`, `edge`, `firefox`) |
| `POST` | `/api/v1/browser/open/{application_id}` | Open application apply URL in a session and return page metadata |
| `GET` | `/api/v1/browser/session/{session_id}` | Get session state for the authenticated user |
| `DELETE` | `/api/v1/browser/session/{session_id}` | Close a session |
| `GET` | `/api/v1/browser/sessions` | List current user's sessions |
| `POST` | `/api/v1/browser/session/{session_id}/restart` | Restart a session (optional browser switch) |
| `GET` | `/api/v1/browser/status` | Browser health summary for dashboard/widget use |

All browser endpoints require authentication and enforce per-user session access.

### Environment configuration

```env
PLAYWRIGHT_BROWSER=chromium
PLAYWRIGHT_HEADLESS=false
PLAYWRIGHT_TIMEOUT=30000
SESSION_IDLE_TIMEOUT=600
MAX_BROWSER_SESSIONS=5
```

### Browser lifecycle flow

1. User creates session -> manager launches Playwright browser/context/page.
2. User opens application -> navigation service resolves URL, waits for load, returns metadata.
3. Manager tracks last activity, current URL, status, and errors.
4. Idle cleanup marks inactive sessions and closes runtime resources.
5. Restart/close APIs explicitly recycle resources for reliability.

## Milestone 11 – Application Management System

### Created files

- [app/db/models/application.py](app/db/models/application.py): Adds `Application` and `ApplicationHistory` with status timeline, favorites, priorities, follow-up date, linked document IDs, and soft-delete support.
- [app/schemas/application.py](app/schemas/application.py): Pydantic contracts for create/update/list/history and status validation.
- [app/services/application_service.py](app/services/application_service.py): Application CRUD, filtered pagination, status-history creation, favorite/priority/notes updates, and linked-document validation.
- [app/api/v1/endpoints/applications.py](app/api/v1/endpoints/applications.py): Application REST endpoints.
- [app/tests/test_applications.py](app/tests/test_applications.py): End-to-end API coverage for create/list/update/favorite/history/delete.

### Updated files

- [app/api/v1/router.py](app/api/v1/router.py): Registers `/api/v1/applications`.
- [app/api/v1/endpoints/__init__.py](app/api/v1/endpoints/__init__.py): Exposes applications router.
- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Registers application models for table creation.
- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py): Extends dashboard statistics with application counters.
- [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds application-related dashboard statistic fields.

### Applications API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/applications` | Create application (draft/ready_to_apply/applied/etc.) |
| `GET` | `/api/v1/applications` | List applications with pagination, filtering, search, sorting, favorites |
| `GET` | `/api/v1/applications/{id}` | Fetch one application |
| `PUT` | `/api/v1/applications/{id}` | Update full application payload |
| `PATCH` | `/api/v1/applications/{id}/favorite` | Toggle favorite |
| `PATCH` | `/api/v1/applications/{id}/notes` | Update notes |
| `PATCH` | `/api/v1/applications/{id}/priority` | Update priority (1–5) |
| `GET` | `/api/v1/applications/{id}/history` | Retrieve status timeline/history |
| `DELETE` | `/api/v1/applications/{id}` | Soft delete by default (`hard_delete=true` for hard delete) |

Supported statuses:
`draft`, `ready_to_apply`, `applied`, `assessment_received`, `interview_scheduled`, `technical_interview`, `hr_interview`, `offer_received`, `offer_accepted`, `offer_declined`, `rejected`, `withdrawn`.

Milestone 11 intentionally does **not** include browser automation, auto form filling, or auto submit.

## Milestone 7 – Automatic Job Aggregation Engine & Smart Dashboard



### Created files



- [app/db/models/aggregation.py](app/db/models/aggregation.py): `AggregationRun` model for storing aggregation execution history and statistics.

- [app/schemas/dashboard.py](app/schemas/dashboard.py): Pydantic schemas for dashboard responses, aggregation history, and notification candidates.

- [app/services/dashboard/aggregation_service.py](app/services/dashboard/aggregation_service.py): Background engine that collects jobs and walk-ins from all providers, handles incremental updates, marks expired jobs, deduplicates, and logs execution statistics.

- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py): Prepares all personalized dashboard sections using the logged-in user's profile, resume, and match scores.

- [app/services/dashboard/notification_prep_service.py](app/services/dashboard/notification_prep_service.py): Identifies notification candidates (new matches, walk-ins, closing soon, high priority) without sending notifications.

- [app/services/dashboard/cache.py](app/services/dashboard/cache.py): In-memory TTL cache for dashboard responses.

- [app/api/v1/endpoints/dashboard.py](app/api/v1/endpoints/dashboard.py): REST endpoints for the smart dashboard and manual aggregation refresh.

- [app/tests/test_aggregation.py](app/tests/test_aggregation.py): Unit tests for the aggregation engine.

- [app/tests/test_dashboard.py](app/tests/test_dashboard.py): Unit and integration tests for dashboard service and API.

- [app/tests/test_aggregation_scheduler.py](app/tests/test_aggregation_scheduler.py): Scheduler tests for full aggregation and dashboard cache refresh.



### Updated files



- [app/core/config.py](app/core/config.py): Adds `JOB_SCHEDULER_ENABLED`, `JOB_REFRESH_INTERVAL_MINUTES`, `AGGREGATION_SCHEDULER_ENABLED`, `DASHBOARD_REFRESH_INTERVAL_MINUTES`, and `DASHBOARD_CACHE_TTL_SECONDS`.

- [app/services/jobs/scheduler.py](app/services/jobs/scheduler.py): Adds `AggregationScheduler`; schedulers now use fresh database sessions per run.

- [app/__init__.py](app/__init__.py): Wires unified aggregation scheduler on application startup.

- [app/api/v1/router.py](app/api/v1/router.py): Registers the dashboard router.

- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Register `AggregationRun` for `init_db()`.

- [app/services/jobs/README.md](app/services/jobs/README.md): Documents aggregation and dashboard architecture.



### Dashboard API



| Method | Path | Description |

|--------|------|-------------|

| `GET` | `/api/v1/dashboard` | Full personalized dashboard (all sections) |

| `GET` | `/api/v1/dashboard/new-jobs` | New jobs from the last 7 days |

| `GET` | `/api/v1/dashboard/recommended` | Recommended jobs based on profile and match scores |

| `GET` | `/api/v1/dashboard/high-matches` | Jobs with 90%+ match scores |

| `GET` | `/api/v1/dashboard/walk-ins` | Personalized walk-in drives |

| `GET` | `/api/v1/dashboard/walk-ins/today` | Today's walk-in drives |

| `GET` | `/api/v1/dashboard/walk-ins/upcoming` | Upcoming walk-in drives |

| `GET` | `/api/v1/dashboard/closing-soon` | Jobs and walk-ins closing soon |

| `GET` | `/api/v1/dashboard/remote` | Remote jobs |

| `GET` | `/api/v1/dashboard/hybrid` | Hybrid jobs |

| `GET` | `/api/v1/dashboard/jobs-by-city` | Job counts grouped by city |

| `GET` | `/api/v1/dashboard/recent-companies` | Recently added companies |

| `GET` | `/api/v1/dashboard/recently-updated` | Recently updated jobs |

| `GET` | `/api/v1/dashboard/statistics` | Dashboard statistics |

| `GET` | `/api/v1/dashboard/notification-candidates` | Notification prep data (no sending) |

| `POST` | `/api/v1/dashboard/refresh` | Recompute user match scores |

| `POST` | `/api/v1/dashboard/aggregate` | Manually trigger full aggregation |

| `GET` | `/api/v1/dashboard/aggregation/history` | Aggregation run history |



All dashboard endpoints require authentication. Results are automatically personalized using the user's skills, education, preferred roles, preferred locations, experience level, active resume, and certifications.



### Scheduler configuration



```env

AGGREGATION_SCHEDULER_ENABLED=true

JOB_SCHEDULER_ENABLED=true

JOB_REFRESH_INTERVAL_MINUTES=60

WALK_IN_REFRESH_INTERVAL_MINUTES=60

DASHBOARD_REFRESH_INTERVAL_MINUTES=30

DASHBOARD_CACHE_TTL_SECONDS=300

```



### Architecture



```

Providers (Job + Walk-in)

        │

        ▼

AggregationService ──► jobs / walk_in_events tables

        │                      │

        │                      ▼

        │               JobMatchService (personalization)

        │                      │

        ▼                      ▼

AggregationRun history   DashboardService ──► /api/v1/dashboard/*

                                │

                                ▼

                     NotificationPrepService (future notifications)

```



New providers can be registered in `AggregationService` without changing dashboard logic.



## Milestone 6.1 – Walk-in Drive Search Module



See [app/services/jobs/README.md](app/services/jobs/README.md) for walk-in architecture details.



### Walk-in API



| Method | Path | Description |

|--------|------|-------------|

| `GET` | `/api/v1/walk-ins` | List/search walk-in drives |

| `GET` | `/api/v1/walk-ins/today` | Today's walk-in drives |

| `GET` | `/api/v1/walk-ins/upcoming` | Upcoming walk-in drives |

| `POST` | `/api/v1/walk-ins/refresh` | Refresh walk-in data from providers |



## Earlier milestones



- Profile and resume management: [app/api/v1/endpoints/profile.py](app/api/v1/endpoints/profile.py), [app/api/v1/endpoints/resumes.py](app/api/v1/endpoints/resumes.py)

- Job search engine: [app/api/v1/endpoints/jobs.py](app/api/v1/endpoints/jobs.py)

- AI job matcher: [app/api/v1/endpoints/matches.py](app/api/v1/endpoints/matches.py)



## Notes



- Resume uploads are stored under the `uploads/resumes` folder.

- Only PDF and DOCX files are accepted, and the maximum size is 5 MB.

- Swagger documentation is available at `/docs` and `/redoc`.

## Milestone 9 – AI Resume Tailoring Engine

### Created files

- [app/db/models/resume_tailoring.py](app/db/models/resume_tailoring.py): Adds `ResumeTemplate`, `TailoredResume`, and `ResumeGenerationHistory` for original resume snapshots, generated versions, ATS score tracking, and status history.
- [app/schemas/resume_tailoring.py](app/schemas/resume_tailoring.py): Pydantic schemas for generation requests, tailored resume reads, and history responses.
- [app/services/resume_tailoring_service.py](app/services/resume_tailoring_service.py): Resume tailoring pipeline with job-signal extraction, ATS-focused improvements, background queue execution, duplicate request caching, output versioning, and multi-format persistence.
- [app/api/v1/endpoints/resume_tailoring.py](app/api/v1/endpoints/resume_tailoring.py): REST endpoints for generation, history, detail, delete, and download.
- [app/tests/test_resume_tailoring.py](app/tests/test_resume_tailoring.py): End-to-end backend/API/generation regression test coverage.

### Updated files

- [app/api/v1/router.py](app/api/v1/router.py): Registers `resume-tailoring` routes.
- [app/api/v1/endpoints/__init__.py](app/api/v1/endpoints/__init__.py): Exposes the resume tailoring endpoint module.
- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Registers new tailoring models for table creation.
- [app/schemas/dashboard.py](app/schemas/dashboard.py): Extends dashboard response with recent generated resumes, ATS average, generation history, and improvement suggestions.
- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py): Injects resume tailoring insights into smart dashboard payloads.

### Resume Tailoring API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/resume-tailoring/generate/{job_id}` | Queue a tailored resume generation run |
| `GET` | `/api/v1/resume-tailoring/history` | Retrieve generation history |
| `GET` | `/api/v1/resume-tailoring/{id}` | Get generation status and tailored resume preview |
| `DELETE` | `/api/v1/resume-tailoring/{id}` | Remove tailored resume and stored outputs |
| `GET` | `/api/v1/resume-tailoring/{id}/download?format=pdf|docx|markdown|html` | Download generated format |

Long-running generations are processed in a background queue, duplicate requests are cached by generation signature, and each resume is versioned per user+job.

## Milestone 10 – AI Cover Letter Generation Engine

### Created files

- [app/db/models/cover_letter.py](app/db/models/cover_letter.py): Adds `CoverLetterTemplate`, `GeneratedCoverLetter`, and `CoverLetterGenerationHistory`.
- [app/schemas/cover_letter.py](app/schemas/cover_letter.py): Pydantic contracts for cover-letter generation, history, templates, and detail responses.
- [app/services/cover_letter_service.py](app/services/cover_letter_service.py): AI-guided cover-letter generation orchestration with queueing, caching, retries, versioning, and multi-format output storage.
- [app/api/v1/endpoints/cover_letters.py](app/api/v1/endpoints/cover_letters.py): REST endpoints for generation, polling, history, template CRUD, download, and delete.
- [app/tests/test_cover_letters.py](app/tests/test_cover_letters.py): End-to-end generation flow test including cache and download.

### Updated files

- [app/api/v1/router.py](app/api/v1/router.py): Registers `cover-letters` routes.
- [app/api/v1/endpoints/__init__.py](app/api/v1/endpoints/__init__.py): Exposes cover-letter endpoint module.
- [app/db/models/__init__.py](app/db/models/__init__.py) and [app/db/session.py](app/db/session.py): Registers cover-letter models.
- [app/services/dashboard/dashboard_service.py](app/services/dashboard/dashboard_service.py): Adds cover-letter dashboard sections and generation statistics.
- [app/schemas/dashboard.py](app/schemas/dashboard.py): Adds cover-letter dashboard response contracts.

### Cover Letter API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/cover-letters/generate/{job_id}` | Queue a company-specific cover-letter generation run |
| `GET` | `/api/v1/cover-letters/history` | Retrieve generation history |
| `GET` | `/api/v1/cover-letters/{id}` | Poll status and retrieve generated content |
| `DELETE` | `/api/v1/cover-letters/{id}` | Delete a generated cover letter and stored outputs |
| `GET` | `/api/v1/cover-letters/{id}/download?format=pdf|docx|markdown|html` | Download generated output |
| `GET` | `/api/v1/cover-letters/templates` | List user templates |
| `POST` | `/api/v1/cover-letters/templates` | Create template |
| `PUT` | `/api/v1/cover-letters/templates/{id}` | Update template |
| `DELETE` | `/api/v1/cover-letters/templates/{id}` | Delete template |

Generation runs in a background executor, failures are retried with status history, duplicate requests are returned from cache by generation signature, and outputs are versioned per user+job.

