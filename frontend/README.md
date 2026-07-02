# Frontend

Vite + React + TypeScript client for the AI Job Assistant.

## Milestone 17 – Interview Preparation UI

### Routes
| Path | Page |
|------|------|
| `/interview-prep/history` | Practice history |
| `/interview-prep/:preparationId` | Preparation preview |
| `/interview-prep/:preparationId/practice` | Mock interview |
| `/interview-prep/:preparationId/feedback` | Session feedback |

### Services & hooks
- `src/services/interviews.service.ts` – API client
- `src/hooks/useInterviews.ts` – React Query hooks (generate, poll, practice, feedback, statistics)

### Components (`src/components/interviews/`)
- `InterviewCard`, `QuestionCard`, `AnswerEditor`, `InterviewProgress`
- `InterviewScoreCard`, `FeedbackCard`, `TopicStrengthChart`, `ReadinessGauge`

### Integrations
- **Job Detail**: “Prepare Interview” button with generate → poll → preview → practice flow
- **Dashboard**: Interview Readiness, Recent Practice Sessions, weakest/strongest topics
- **Applications**: interview readiness indicators on application cards
- **Sidebar**: Interview Prep navigation link

### Tests
```bash
npm test
npm run build
npm run lint
```

Test files:
- `src/test/hooks/useInterviews.test.tsx`
- `src/test/components/InterviewPracticePage.test.tsx`
- `src/test/components/InterviewFeedbackPage.test.tsx`
