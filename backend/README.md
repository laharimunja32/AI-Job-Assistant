# Backend

FastAPI backend for the AI Job Assistant.

## Milestone 21 – Live Job Search & Browser Application

### Models
- `app/db/models/job_search.py` – `LiveJobSearch` (per-user search history)
- `app/db/models/saved_job.py` – `SavedJob` (bookmarked jobs)
- `app/db/models/application_history.py` – `BrowserAutomationRecord` (automation runs)

### Services
- `app/services/job_search_service.py` – Live search with filters, pagination, provider orchestration
- `app/services/saved_job_service.py` – Save, remove, list, status check
- `app/services/browser_application_service.py` – Full apply flow reusing Playwright services in `app/services/browser/`

### API
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/job-search/search` | Live job search |
| GET | `/api/v1/job-search/history` | Search history |
| GET | `/api/v1/job-search/{id}` | Search detail |
| POST | `/api/v1/saved-jobs` | Save job |
| DELETE | `/api/v1/saved-jobs/{id}` | Remove saved job |
| GET | `/api/v1/saved-jobs` | List saved jobs |
| GET | `/api/v1/saved-jobs/status/check` | Check saved status |
| POST | `/api/v1/browser-application/start` | Start automation |
| POST | `/api/v1/browser-application/{id}/submit` | Submit application |
| GET | `/api/v1/browser-application/history` | Automation history |
| GET | `/api/v1/browser-application/{id}` | Automation detail |

`BrowserManager` is initialized on app startup via lifespan in `app/__init__.py`.

### Tests
```bash
python -m pytest backend/app/tests/test_job_search.py backend/app/tests/test_saved_jobs.py backend/app/tests/test_browser_application.py
```

## Milestone 20 – Cover Letter Generator

### Model (`app/db/models/cover_letter_generator.py`)
- `CoverLetter` – stores generated letters with resume/JD context, template, tone, length, and file paths

### Service (`app/services/cover_letter_generator_service.py`)
- Extracts skills from resume and keywords from job description
- Generates introduction, experience section, skills alignment, and closing
- Never invents experience — only uses resume/profile data
- Templates: `professional`, `modern`, `simple`
- Tones: `professional`, `friendly`, `formal`, `confident`
- Lengths: `short`, `medium`, `long`
- PDF/DOCX output in `uploads/cover_letters_generator/`

### API (`app/api/v1/endpoints/cover_letter_generator.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cover-letter-generator/generate` | Generate cover letter |
| GET | `/api/v1/cover-letter-generator/history` | List letters |
| GET | `/api/v1/cover-letter-generator/{id}` | Get letter detail |
| PUT | `/api/v1/cover-letter-generator/{id}` | Update letter content |
| DELETE | `/api/v1/cover-letter-generator/{id}` | Delete letter |
| GET | `/api/v1/cover-letter-generator/{id}/download` | Download PDF/DOCX |

### Dashboard integration
Extended `app/schemas/dashboard.py` and `app/services/dashboard/dashboard_service.py` with:
- `cover_letter_generator_statistics` (total, this week, most used template)
- `latest_cover_letter_generator`, `recent_cover_letter_generators`

### Tests
```bash
python -m pytest backend/app/tests/test_cover_letter_generator.py
```

> The existing job-based cover letter module (`app/services/cover_letter_service.py`, `/api/v1/cover-letters`) is unchanged.

## Milestone 19 – Resume Optimizer

### Model (`app/db/models/resume_optimization.py`)
- `ResumeOptimization` – stores ATS analysis results, scores, keywords, skills, recommendations, tailored resume text

### Service (`app/services/resume_optimizer_service.py`)
- Parses resume text and job description
- Compares skills/keywords against verified user inventory (profile + resume)
- Computes ATS, keyword, skill, experience, education, and overall scores
- Generates tailored resume without inventing credentials
- PDF/DOCX output in `uploads/optimized_resumes/`

### API (`app/api/v1/endpoints/resume_optimizer.py`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resume-optimizer/analyze` | Analyze resume vs JD |
| GET | `/api/v1/resume-optimizer/history` | List analyses |
| GET | `/api/v1/resume-optimizer/{analysis_id}` | Get full analysis |
| DELETE | `/api/v1/resume-optimizer/{analysis_id}` | Delete analysis |
| GET | `/api/v1/resume-optimizer/{analysis_id}/download` | Download PDF/DOCX |

### Tests
```bash
python -m pytest backend/app/tests/test_resume_optimizer.py
```

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
