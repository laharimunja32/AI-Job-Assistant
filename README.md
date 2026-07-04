# AI Job Application Assistant

Full-stack AI-powered job application platform with resume tailoring, ATS resume optimization, cover letters, AI cover letter generator, applications, browser automation, recruitment monitoring, and **AI interview preparation**.

## Milestone 20 – AI Cover Letter Generator

### Workflow
1. Upload a master resume (`/resumes`)
2. Open **Cover Letter Generator** from the sidebar
3. Enter job title, company name, and paste the job description
4. Choose template (Professional, Modern, Simple), tone, and length
5. Generate (`POST /api/v1/cover-letter-generator/generate`)
6. Edit the letter, preview, save changes, and download PDF or DOCX

### Templates
| Template | Style |
|----------|-------|
| Professional | Classic business format with clear sections |
| Modern | Clean headings with structured sections |
| Simple | Minimal formatting, direct paragraphs |

### Tones & Lengths
- **Tones**: Professional, Friendly, Formal, Confident
- **Lengths**: Short (~1 paragraph), Medium (balanced), Long (detailed with profile context)

### Architecture
- **Backend model**: `CoverLetter` (`backend/app/db/models/cover_letter_generator.py`)
- **Service**: `backend/app/services/cover_letter_generator_service.py`
- **API**: `backend/app/api/v1/endpoints/cover_letter_generator.py`
- **Frontend**: pages under `frontend/src/pages/cover-letter-generator/`, hooks `useCoverLetterGenerator`, service `coverLetterGenerator.service.ts`
- **Dashboard**: Cover Letter Analytics (total generated, this week, most used template, latest, recent list)

> **Note**: The existing job-based cover letter module (`/api/v1/cover-letters`) remains unchanged and is used from Job Detail pages.

### API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/v1/cover-letter-generator/generate` | Generate cover letter |
| GET | `/api/v1/cover-letter-generator/history` | List past letters |
| GET | `/api/v1/cover-letter-generator/{id}` | Full letter detail |
| PUT | `/api/v1/cover-letter-generator/{id}` | Update letter content |
| DELETE | `/api/v1/cover-letter-generator/{id}` | Delete letter |
| GET | `/api/v1/cover-letter-generator/{id}/download?format=pdf\|docx` | Download letter |

### Example Generate Request
```json
{
  "resume_id": 1,
  "job_description": "Backend Engineer. Python, FastAPI, SQL, Docker required.",
  "job_title": "Backend Engineer",
  "company_name": "Acme Corp",
  "template_name": "professional",
  "tone": "professional",
  "length": "medium"
}
```

### Frontend Routes
- `/cover-letter-generator` — new generation form
- `/cover-letter-generator/history` — past letters
- `/cover-letter-generator/:id` — edit, preview, download

### Testing
```bash
python -m pytest backend/app/tests/test_cover_letter_generator.py
cd frontend && npm test && npm run build
```

## Milestone 19 – AI Resume Tailoring & ATS Optimization

### Workflow
1. Upload a master resume (`/resumes`)
2. Open **Resume Optimizer** and paste a job description
3. Run analysis (`POST /api/v1/resume-optimizer/analyze`)
4. Review ATS score, keyword gaps, skill match, and recommendations
5. Preview the tailored resume (only uses skills/experience you already have)
6. Download optimized PDF or DOCX

### Architecture
- **Backend model**: `ResumeOptimization` (`backend/app/db/models/resume_optimization.py`)
- **Service**: `backend/app/services/resume_optimizer_service.py`
- **API**: `backend/app/api/v1/endpoints/resume_optimizer.py`
- **Schemas**: `backend/app/schemas/resume_optimizer.py`
- **Frontend**: pages under `frontend/src/pages/resume-optimizer/`, hooks `useResumeOptimizer`, service `resumeOptimizer.service.ts`
- **Dashboard**: Resume Analytics section (average/highest ATS, latest optimization, recent list)

### API Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/v1/resume-optimizer/analyze` | Analyze resume vs job description |
| GET | `/api/v1/resume-optimizer/history` | List past analyses |
| GET | `/api/v1/resume-optimizer/{analysis_id}` | Full analysis detail |
| DELETE | `/api/v1/resume-optimizer/{analysis_id}` | Delete analysis |
| GET | `/api/v1/resume-optimizer/{analysis_id}/download?format=pdf\|docx` | Download tailored resume |

### Example Analyze Request
```json
{
  "resume_id": 1,
  "job_description": "Backend Engineer. Python, FastAPI, SQL, Docker required. 3+ years.",
  "job_title": "Backend Engineer",
  "company_name": "Acme Corp"
}
```

### Example Analyze Response
```json
{
  "id": 12,
  "ats_score": 88,
  "overall_score": 87,
  "keyword_match": 82,
  "skill_match": 91,
  "experience_match": 80,
  "education_match": 100,
  "matched_keywords": ["Python", "FastAPI"],
  "missing_keywords": ["Kubernetes"],
  "matched_skills": ["Python", "SQL", "Docker"],
  "missing_skills": ["Terraform"],
  "recommendations": ["Mirror job-description terminology in your summary."],
  "tailored_resume": "# Optimized Resume — Backend Engineer\n..."
}
```

### Frontend Routes
- `/resume-optimizer` — new analysis
- `/resume-optimizer/history` — past optimizations
- `/resume-optimizer/:id` — detail view with charts and downloads

### Testing
```bash
python -m pytest backend/app/tests/test_resume_optimizer.py
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
