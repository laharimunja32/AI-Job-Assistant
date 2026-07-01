# Job Search Engine

This package contains the modular job discovery pipeline for the backend.

## Structure

- parser_service.py: normalizes provider payloads into the internal job schema.
- duplicate_detection_service.py: detects likely duplicates by URL or normalized identity fields.
- search_service.py: orchestrates provider calls, persistence, filtering, and history logging.
- providers/base.py: abstract contract for new job sources.
- providers/sample_provider.py: a deterministic sample provider for local development and tests.
- scheduler.py: APScheduler-based wrapper for recurring searches.

## Adding a New Source

1. Implement a subclass of JobProvider in app/services/jobs/providers.
2. Return a list of dictionaries with the normalized fields expected by the parser.
3. Register the provider in the service wiring for the relevant endpoint or background job.

## Notes

The initial implementation focuses on a generic provider interface and a sample provider so the architecture remains extensible for future integrations.
