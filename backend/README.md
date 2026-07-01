# Backend

This module contains the FastAPI backend for the AI Job Assistant. The current milestone adds a production-ready profile and resume management layer with persistent storage, validation, pagination, and REST endpoints.

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
