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

## Milestone 18 – Interview Feedback System

### Workflow
1. Complete a mock interview session (Milestone 17 practice flow)
2. Evaluate the session (`POST /api/v1/interview-feedback/evaluate`)
3. Review feedback history and progress analytics
4. Open individual feedback records for detailed scores, radar charts, and per-question reviews
5. Delete outdated feedback records when needed

### Interview Feedback APIs
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/interview-feedback/evaluate` | Evaluate a completed session and return feedback detail |
| GET | `/api/v1/interview-feedback/history` | Paginated feedback history (`page`, `size`) |
| GET | `/api/v1/interview-feedback/progress` | Aggregated scores, skills, trends, and breakdown |
| GET | `/api/v1/interview-feedback/{feedback_id}` | Full feedback detail with question reviews |
| DELETE | `/api/v1/interview-feedback/{feedback_id}` | Delete a feedback record |

### Example API Requests
```bash
# Evaluate a completed session
curl -X POST http://localhost:8000/api/v1/interview-feedback/evaluate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 12}'

# Progress analytics for dashboard widgets
curl http://localhost:8000/api/v1/interview-feedback/progress \
  -H "Authorization: Bearer $TOKEN"

# Paginated history
curl "http://localhost:8000/api/v1/interview-feedback/history?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"

# Feedback detail
curl http://localhost:8000/api/v1/interview-feedback/5 \
  -H "Authorization: Bearer $TOKEN"
```

### Architecture
- **Backend service**: `backend/app/services/interview_feedback_service.py`
- **API**: `backend/app/api/v1/endpoints/interview_feedback.py`
- **Schemas**: `backend/app/schemas/interview_feedback.py`
- **Frontend service**: `frontend/src/services/interview-feedback.service.ts`
- **Hooks**: `frontend/src/hooks/useInterviewFeedback.ts`
- **Pages**: `frontend/src/pages/interview-feedback/`
- **Charts**: `FeedbackProgressChart`, `SkillDistributionChart`, `PerformanceBreakdown`, `FeedbackRadarChart`

### Frontend Routes
| Route | Page |
|-------|------|
| `/interview-feedback` | Feedback history, progress charts, and analytics |
| `/interview-feedback/:feedbackId` | Detailed feedback with scores, radar chart, and question reviews |

Milestone 17 routes (`/interview-prep/*`) remain unchanged for preparation and legacy per-session feedback.

### Dashboard Integration
The dashboard includes an **Interview Feedback** section powered by `GET /interview-feedback/progress` and recent history cards:
- Average / best / latest interview scores
- Completed interviews count
- Strongest and weakest skills
- Recent feedback cards linking to `/interview-feedback/:feedbackId`

### Testing
```bash
# Backend
python -m pytest backend/app/tests/test_interview_feedback.py

# Frontend
cd frontend && npm test -- src/test/hooks/useInterviewFeedback.test.tsx src/test/components/InterviewFeedbackListPage.test.tsx src/test/components/InterviewFeedbackDetailPage.test.tsx

# TypeScript + production build
cd frontend && npm run lint && npm run build
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
