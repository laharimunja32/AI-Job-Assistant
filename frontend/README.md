# AI Job Assistant — Frontend

Production-ready React frontend for the AI Job Application Assistant platform. Consumes the existing FastAPI backend — no mock data, no duplicate business logic.

## Tech Stack

- React 19 · Vite · TypeScript
- Tailwind CSS · Framer Motion · Recharts
- React Router · Axios · TanStack Query
- Zustand · React Hook Form · Zod

## Quick Start

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

**Prerequisites:** Start the backend from the `backend/` directory first.

```bash
cd backend
uvicorn main:app --reload
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Type-check and production build |
| `npm run preview` | Preview production build |
| `npm test` | Run Vitest tests |
| `npm run lint` | TypeScript check |

## Environment

Optional `.env` in `frontend/`:

```
VITE_API_BASE_URL=/api/v1
```

Defaults to `/api/v1` (Vite proxy in development).

---

## Folder Structure

```
src/
├── assets/          # Static images and icons (extend as needed)
├── components/      # Reusable UI and feature components
│   ├── ui/          # Primitives: Button, Card, Modal, etc.
│   ├── layout/      # Sidebar, TopNav
│   ├── jobs/        # JobCard, JobListGrid
│   ├── walk-ins/    # WalkInCard
│   ├── dashboard/   # StatCard, DashboardSection
│   └── cover-letters/ # Cover letter generation UI components
├── contexts/        # React contexts (Toast)
├── hooks/           # TanStack Query hooks per domain
├── layouts/         # AppLayout, AuthLayout
├── pages/           # Route-level page components
├── routes/          # Router config, ProtectedRoute
├── services/        # Axios API layer (centralized)
├── store/           # Zustand global state
├── styles/          # Global CSS and Tailwind
├── test/            # Vitest tests
├── types/           # TypeScript API types
└── utils/           # Helpers (cn, formatDate, storage)
```

---

## Pages

| Route | Page | Backend APIs |
|-------|------|--------------|
| `/` | **Dashboard** | `GET /dashboard` — auto-loads personalized feed |
| `/login` | Login | `POST /auth/login` |
| `/register` | Register | `POST /auth/register` |
| `/forgot-password` | Forgot Password | UI placeholder (future endpoint) |
| `/jobs` | Jobs list | `GET /jobs/all`, `GET /dashboard/high-matches` |
| `/jobs/:id` | Job detail | `GET /jobs/all`, `POST /matches/jobs/:id`, `POST /resume-tailoring/generate/:id`, `POST /cover-letters/generate/:id`, `POST /applications` (Prepare Application) |
| `/walk-ins` | Walk-ins | `GET /walk-ins`, `/today`, `/upcoming` |
| `/walk-ins/:id` | Walk-in detail | `GET /walk-ins` |
| `/resumes` | Resume list | `GET /resumes`, `POST /resumes` |
| `/resumes/:id` | Resume detail | `GET /resumes`, download, activate |
| `/profile` | Profile editor | `GET/PUT /profile` |
| `/applications` | Applications manager | `GET/POST/PUT/PATCH/DELETE /applications`, `GET /applications/:id/history` |
| `/notifications` | Notification center | `GET /dashboard/notification-candidates` |
| `/settings` | Settings | Health, aggregation, theme |
| `/browser-automation` | Browser automation foundation | `POST/GET/DELETE /browser/*`, `POST /browser/open/:application_id` |
| `/form-assistant` | Intelligent form detection & auto-fill | `POST /browser/forms/detect/:session_id`, `POST /browser/forms/fill/:session_id`, `GET /browser/forms/report/:session_id` |
| `/upload-assistant` | Intelligent resume & cover-letter upload assistant | `POST /browser/uploads/detect/:session_id`, `POST /browser/uploads/all/:session_id`, `GET /browser/uploads/status/:session_id`, `POST /browser/uploads/retry/:session_id` |
| `/review-assistant` | Guided review and assisted submission | `GET /browser/review/:session_id`, `POST /browser/review/validate/:session_id`, `POST /browser/review/confirm/:session_id`, `GET /browser/review/history/:application_id` |
| `/recruitment-emails` | Recruitment emails monitor | `GET /emails`, `POST /emails/process`, `GET /emails/:id` |
| `/assessments` | Assessments tracker | `GET/POST/PUT /assessments` |
| `/interviews` | Interview tracker | `GET/POST/PUT /interviews` |
| `/timeline` | Unified application timeline | `GET /timeline/:application_id` |
| `/reminders` | Reminder manager | `GET/POST/PUT/DELETE /reminders` |

### Dashboard (Home)

After login, the dashboard **automatically loads** without search:

- New jobs, high matches, recommendations
- Walk-ins (all, today, upcoming)
- Remote & hybrid jobs
- Closing soon, recent companies
- Statistics & jobs-by-city chart
- Refresh matches via `POST /dashboard/refresh`

---

## Reusable Components

### UI Primitives (`components/ui/`)

| Component | Purpose |
|-----------|---------|
| `Button` | Primary actions with variants and loading state |
| `Card` | Content container with optional header |
| `Badge` / `MatchScoreBadge` | Status and AI match score display |
| `Input` / `Textarea` / `Select` | Form controls with labels and errors |
| `Loader` / `Spinner` / `Skeleton` | Loading states |
| `EmptyState` / `ErrorState` | Empty and error UX |
| `Pagination` | Page navigation for lists |
| `Modal` / `ConfirmDialog` | Dialogs and confirmations |
| `Chip` | Removable tags (skills, locations) |
| `Toast` / `ToastContainer` | Toast notifications |

### Feature Components

| Component | Purpose |
|-----------|---------|
| `JobCard` | Job listing card with bookmark and match badge |
| `WalkInCard` | Walk-in drive card with venue and register link |
| `StatCard` / `DashboardStats` | Dashboard metric tiles |
| `DashboardSection` | Section wrapper with "View all" link |
| `Sidebar` | Left navigation |
| `TopNav` | Top bar with theme, notifications, user menu |

---

## State Management

| Store | Purpose |
|-------|---------|
| `authStore` | JWT tokens, login/logout, session persistence |
| `uiStore` | Theme (light/dark/system), sidebar state |
| `bookmarksStore` | Saved/bookmarked jobs (local until backend) |
| `applicationsStore` | Legacy local tracker store (kept for compatibility) |

Server data uses **TanStack Query** with centralized hooks in `hooks/`.

---

## Authentication

- Login / register via backend JWT endpoints
- Access + refresh tokens in `localStorage`
- Axios interceptor auto-refreshes on 401
- `ProtectedRoute` guards authenticated pages
- Logout revokes refresh token via `POST /auth/logout`

---

## Placeholder Features (Future Milestones)

These UI elements are present but not fully backend-persistent yet:

- **Forgot Password** — auth flow
- **Password Change** — settings
- **Advanced browser automation (form fill/upload/submit/CAPTCHA)** — intentionally deferred to next milestone
- **Email notification delivery** — prep data shown, sending TBD

## Milestone 16 – Email & Assessment Monitoring

Milestone 16 adds recruitment communication tracking pages and dashboard summary cards:

- `pages/recruitment/RecruitmentEmailsPage.tsx`: authorized email processing UI + search/filter/sort + event badges.
- `pages/recruitment/AssessmentsPage.tsx`: status tracking, deadline indicators, list/calendar views.
- `pages/recruitment/InterviewsPage.tsx`: interview status and scheduling tracker.
- `pages/recruitment/TimelinePage.tsx`: unified application event stream.
- `pages/recruitment/RemindersPage.tsx`: reminder CRUD and due indicators.
- `hooks/useRecruitmentMonitoring.ts`, `services/recruitmentMonitoring.service.ts`, `types/api.ts`: integration layer for all monitoring endpoints.
- Dashboard now surfaces upcoming assessments/interviews, offers/rejections, unread recruitment emails, and today’s deadlines.

## Milestone 15 – Guided Review & Assisted Submission

Milestone 15 adds a dedicated Guided Review page to complete the final pre-submit workflow:

- New page: `pages/browser/ReviewAssistantPage.tsx`
- Route + navigation entry: `/review-assistant`
- Key actions:
  - Edit detected values (overrides) and re-run auto-fill
  - Re-run document uploads
  - Refresh validation report
  - Explicitly confirm review
  - Proceed to submission attempt only after confirmation dialog
- API integration:
  - `services/browser.service.ts` now includes review/validate/confirm/history endpoints
  - `hooks/useBrowserAutomation.ts` includes review-specific query/mutation hooks
- Dashboard stats now include review-centric counters:
  - ready to submit
  - applications under review
  - submitted today
  - validation failures
  - average readiness score

## Milestone 11 – Application Management

Milestone 11 introduces a fully backend-persistent application workflow:

- Application list with pagination, filter, status tabs, search, favorites, and sorting (`pages/applications/ApplicationsPage.tsx`)
- Application details panel with status updates, priority selector, notes editor, delete, and timeline/history
- Job detail “Prepare Application” flow with explicit document linking (`pages/jobs/JobDetailPage.tsx`)
- API and query layer: `services/applications.service.ts`, `hooks/useApplications.ts`, `types/api.ts`
- Dashboard stats now include application counters (`components/dashboard/StatCard.tsx`)

Out of scope for this milestone:

- Browser automation
- Form auto-fill/upload automation
- CAPTCHA handling
- Auto submit

## Milestone 12 – Browser Automation Foundation

Milestone 12 adds a dedicated Browser Automation page and API integration for Playwright session lifecycle management:

- Browser automation control center: `pages/browser/BrowserAutomationPage.tsx`
- API integration: `services/browser.service.ts`
- Query hooks: `hooks/useBrowserAutomation.ts`
- Type contracts: `types/api.ts` (`BrowserSession`, `BrowserStatusSummary`, metadata)
- Dashboard widget integration: browser health and activity stats are shown on `pages/dashboard/DashboardPage.tsx`
- Navigation entry: `components/layout/Sidebar.tsx`, route in `routes/index.tsx`
- Tests: `test/hooks/useBrowserAutomation.test.tsx`, `test/components/BrowserAutomationPage.test.tsx`

This milestone is foundational only: it launches/restarts/closes sessions and opens application pages, but does not fill or submit forms.

## Milestone 13 – Intelligent Form Detection & Auto-Fill

Milestone 13 adds a dedicated Form Assistant experience for profile-based field mapping and controlled auto-fill:

- New page: `pages/browser/FormAssistantPage.tsx`
- Route + sidebar entry: `/form-assistant`
- Browser automation APIs integrated:
  - detect fields by session
  - auto-fill supported mapped values
  - fetch latest fill report
- Hooks: `hooks/useBrowserAutomation.ts` (`useDetectFormFields`, `useFillFormFields`, `useFormFillReport`)
- API layer: `services/browser.service.ts` form methods
- Types: `types/api.ts` form detection/fill contracts
- Dashboard browser widget now includes:
  - forms detected
  - fields filled
  - manual fields remaining
  - average fill success rate

Out of scope in this milestone:

- Resume upload automation
- Cover letter upload automation
- CAPTCHA solving
- Auto-submit

## Milestone 14 – Intelligent Upload Assistant

Milestone 14 adds guided upload automation in the browser workflow:

- New page: `pages/browser/UploadAssistantPage.tsx`
- Route + sidebar entry: `/upload-assistant`
- Hooks: `hooks/useBrowserAutomation.ts` (`useDetectUploadFields`, `useUploadAllDocuments`, `useUploadStatus`, `useRetryUpload`)
- API integration: `services/browser.service.ts` upload methods
- Types: `types/api.ts` upload detection/status/validation contracts
- Tests: `test/components/UploadAssistantPage.test.tsx`

Upload Assistant UI surfaces:

- detected upload fields
- selected application documents (resume/tailored/cover letter ids)
- upload progress and current status
- uploaded filename and validation/error feedback
- retry action for failed uploads

Dashboard browser metrics are extended with upload statistics:

- successful uploads
- failed uploads
- resume upload count
- cover letter upload count
- average upload time

---

## Testing

```bash
npm test
```

- `test/components/` — component unit tests
- `test/routes/` — route guard tests
- `test/hooks/` — API hook tests with mocked services

---

## Architecture Notes

- **Lazy loading** — all pages code-split via `React.lazy`
- **No mock data** — every data view calls real backend APIs
- **Vite proxy** — avoids CORS issues in development
- **Extensible** — services/hooks pattern supports new backend modules
