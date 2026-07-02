# Job Search Engine

This package contains the modular job discovery pipeline for the backend, including standard job search, walk-in drive discovery, and the automatic aggregation engine.

## Structure

### Standard jobs

- `parser_service.py`: normalizes provider payloads into the internal job schema.
- `duplicate_detection_service.py`: detects likely duplicates by URL or normalized identity fields.
- `search_service.py`: orchestrates provider calls, persistence, filtering, and history logging.
- `match_service.py`: evaluates profile-to-job compatibility, persists match results, and suggests profile or resume improvements.
- `providers/base.py`: abstract contract for new job sources.
- `providers/sample_provider.py`: a deterministic sample provider for local development and tests.
- `scheduler.py`: APScheduler wrappers for recurring job searches, walk-in refresh, and unified aggregation (`SearchScheduler`, `WalkInScheduler`, `AggregationScheduler`).

### Walk-in drives

- `walk_in_parser_service.py`: normalizes walk-in provider payloads into the internal walk-in schema.
- `walk_in_duplicate_detection_service.py`: detects duplicate walk-in events by registration URL or normalized identity fields.
- `walk_in_service.py`: orchestrates walk-in provider calls, persistence, filtering, expired-event cleanup, and sync into the shared `jobs` table for AI matching.
- `providers/walkin_provider.py`: abstract contract (`WalkInProvider`) and `SampleWalkInProvider` for local development and tests.

### Dashboard and aggregation (`app/services/dashboard/`)

- `aggregation_service.py`: background engine that collects jobs and walk-ins from all providers, marks expired entries, deduplicates, and records `AggregationRun` history.
- `dashboard_service.py`: prepares personalized dashboard sections using profile, resume, and match scores.
- `notification_prep_service.py`: identifies notification candidates (new matches, walk-ins, closing soon, high priority) without sending notifications.
- `cache.py`: in-memory TTL cache for dashboard responses.

## Adding a New Job Source

1. Implement a subclass of `JobProvider` in `app/services/jobs/providers`.
2. Return a list of dictionaries with the normalized fields expected by the parser.
3. Register the provider in the aggregation service wiring (see `app/api/v1/endpoints/dashboard.py` or `scheduler.py`).

## Adding a New Walk-in Source

1. Implement a subclass of `WalkInProvider` in `app/services/jobs/providers`.
2. Return dictionaries with fields such as `company_name`, `job_role`, `venue`, `city`, `walk_in_date`, `skills`, and `registration_url`.
3. Register the provider in `WalkInEventService` or `AggregationService` wiring.

## Walk-in to AI Matcher Bridge

Walk-in events are synced into the shared `Job` table with `external_id=walkin:{event_id}` and `employment_type=Walk-in`. The existing `JobMatchService` can score them without any matcher changes.

## API Endpoints

### Walk-ins

- `GET /api/v1/walk-ins`: list and search walk-in drives
- `GET /api/v1/walk-ins/today`: today's walk-in drives
- `GET /api/v1/walk-ins/upcoming`: upcoming walk-in drives
- `POST /api/v1/walk-ins/refresh`: refresh data from registered providers

### Dashboard (Milestone 7)

- `GET /api/v1/dashboard`: full personalized dashboard
- `GET /api/v1/dashboard/new-jobs`: recently added jobs
- `GET /api/v1/dashboard/recommended`: recommended jobs based on profile and match scores
- `GET /api/v1/dashboard/high-matches`: jobs with 90%+ match scores
- `GET /api/v1/dashboard/walk-ins`: personalized walk-in drives
- `GET /api/v1/dashboard/closing-soon`: jobs and walk-ins closing soon
- `GET /api/v1/dashboard/remote`: remote jobs
- `GET /api/v1/dashboard/statistics`: dashboard statistics
- `GET /api/v1/dashboard/recent-companies`: recently added companies
- `POST /api/v1/dashboard/refresh`: recompute user matches
- `POST /api/v1/dashboard/aggregate`: manually trigger full aggregation

## Scheduler

Enable automatic aggregation with environment variables:

```env
AGGREGATION_SCHEDULER_ENABLED=true
JOB_SCHEDULER_ENABLED=true
JOB_REFRESH_INTERVAL_MINUTES=60
WALK_IN_REFRESH_INTERVAL_MINUTES=60
DASHBOARD_REFRESH_INTERVAL_MINUTES=30
```

Legacy walk-in-only scheduler (used when `AGGREGATION_SCHEDULER_ENABLED=false`):

```env
WALK_IN_SCHEDULER_ENABLED=true
WALK_IN_REFRESH_INTERVAL_MINUTES=60
```

## Notes

The architecture uses provider interfaces so new sources can be added without changing the dashboard or aggregation logic. The dashboard automatically personalizes results using skills, education, preferred roles, locations, experience level, active resume, and certifications from the user's profile.
