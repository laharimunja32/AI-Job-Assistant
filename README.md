# AI Job Application Assistant

Full-stack AI-powered job application platform with resume tailoring, cover letters, applications, browser automation, recruitment monitoring, and **AI interview preparation**.

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
