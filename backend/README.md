# Backend

FastAPI backend for the AI Job Assistant.

## Milestone 17 – Interview Preparation

### Models (`app/db/models/interview.py`)
- `InterviewPreparation` – AI-generated prep package with scores, topics, versioning, cache signature
- `InterviewQuestion` – categorized questions (company, HR, behavioral, technical, project, resume)
- `InterviewAnswer` – per-question user answers with AI scoring
- `InterviewFeedback` – aggregated session feedback
- `InterviewSession` – interactive mock interview state

### Service (`app/services/interview_service.py`)
- Generation from job description, resume, tailored resume, cover letter, profile, skills, ATS keywords
- Background queue via `ThreadPoolExecutor` with `queued → processing → completed | failed`
- Cache reuse by user/job/resume/profile/cover-letter versions (`generation_signature`)
- Session lifecycle: start, answer, finish, history, statistics
- Dashboard helpers: `recent_for_dashboard()`, `stats_for_dashboard()`

### API (`app/api/v1/endpoints/interviews.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/interviews/generate/{job_id}` | Generate preparation |
| GET | `/api/v1/interviews/history` | Practice history |
| GET | `/api/v1/interviews/statistics` | Aggregate stats |
| GET | `/api/v1/interviews/{id}` | Get preparation + questions |
| DELETE | `/api/v1/interviews/{id}` | Delete preparation |
| POST | `/api/v1/interviews/{id}/start` | Start practice session |
| POST | `/api/v1/interviews/{id}/answer` | Submit answer |
| POST | `/api/v1/interviews/{id}/finish` | Finish session |
| GET | `/api/v1/interviews/{id}/feedback` | Get feedback |

All endpoints require authentication and enforce per-user ownership.

### Dashboard integration
Extended `app/schemas/dashboard.py` and `app/services/dashboard/dashboard_service.py` with:
- `recent_interviews`, `interview_statistics`
- `average_interview_readiness`, `average_interview_confidence`, `interview_practice_sessions`, `interview_questions_answered`

### Tests
```bash
python -m pytest backend/app/tests/test_interviews.py
```

## Earlier milestones

## Created files

- [app/api/v1/endpoints/profile.py](app/api/v1/endpoints/profile.py): Implements profile CRUD and profile deletion endpoints.
- [app/api/v1/endpoints/resumes.py](app/api/v1/endpoints/resumes.py): Implements resume upload, listing, download, activation, and deletion endpoints.
- [app/db/models/profile.py](app/db/models/profile.py): Defines the persisted user profile table and its relationship to the user account.
- [app/db/models/resume.py](app/db/models/resume.py): Defines the persisted resume table, including versioning and active-resume tracking.
- [app/schemas/profile.py](app/schemas/profile.py): Provides request and response schemas for profile data.
- [app/schemas/resume.py](app/schemas/resume.py): Provides request and response schemas for resume metadata and list responses.
- [app/services/profile_service.py](app/services/profile_service.py): Contains the business logic for validation, persistence, duplicate detection, and file handling.
- [app/tests/test_profile_resume.py](app/tests/test_profile_resume.py): Covers profile CRUD and end-to-end resume upload and deletion flows.

## Notes

- Resume uploads are stored under the uploads/resumes folder.
- Only PDF and DOCX files are accepted, and the maximum size is 5 MB.
- Swagger documentation is available through the FastAPI docs routes at /docs and /redoc.
