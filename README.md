# AI Job Application Assistant

Full-stack AI-powered job application platform with resume tailoring, ATS resume optimization, cover letters, applications, browser automation, recruitment monitoring, and **AI interview preparation**.

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
