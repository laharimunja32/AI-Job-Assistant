from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.user import User
from app.schemas.profile import ProfileCreateUpdate

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "resumes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


def _serialize_for_json(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_serialize_for_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_for_json(item) for key, item in value.items()}
    return value


def get_or_create_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        profile = Profile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def upsert_profile(db: Session, user: User, profile_data: ProfileCreateUpdate) -> Profile:
    profile = get_or_create_profile(db, user)

    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name

    for field in [
        "phone",
        "address",
        "location",
        "education",
        "skills",
        "certifications",
        "projects",
        "work_preferences",
        "preferred_job_roles",
        "preferred_locations",
        "linkedin_url",
        "github_url",
        "portfolio_url",
    ]:
        value = getattr(profile_data, field, None)
        if value is not None:
            setattr(profile, field, _serialize_for_json(value))

    db.add(user)
    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    return profile


def delete_profile(db: Session, user: User) -> None:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is not None:
        db.delete(profile)
        db.commit()


def _validate_upload(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF and DOCX files are supported")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds maximum size of 5MB")


def _duplicate_resume_exists(db: Session, user: User, filename: str) -> bool:
    return db.query(Resume).filter(Resume.user_id == user.id, Resume.filename == filename).first() is not None


def create_resume(db: Session, user: User, file: UploadFile) -> Resume:
    _validate_upload(file)
    if _duplicate_resume_exists(db, user, file.filename or "resume"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A resume with the same filename already exists")

    file_bytes = file.file.read()
    file.file.seek(0)
    existing_resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    version = max((resume.version for resume in existing_resumes), default=0) + 1
    storage_name = f"{user.id}_{len(existing_resumes) + 1}_{file.filename}"
    storage_path = UPLOAD_DIR / storage_name
    storage_path.write_bytes(file_bytes)

    resume = Resume(
        user_id=user.id,
        filename=file.filename or "resume",
        content_type=file.content_type or "application/octet-stream",
        file_size=len(file_bytes),
        storage_path=str(storage_path),
        version=version,
        is_active=True,
        file_metadata={"source": "upload"},
    )

    existing_active = db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active.is_(True)).first()
    if existing_active is not None:
        existing_active.is_active = False
        db.add(existing_active)

    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session, user: User, page: int, size: int, active: bool | None = None, filename_contains: str | None = None) -> tuple[list[Resume], int]:
    query = db.query(Resume).filter(Resume.user_id == user.id)
    if active is not None:
        query = query.filter(Resume.is_active.is_(active))
    if filename_contains:
        query = query.filter(Resume.filename.ilike(f"%{filename_contains}%"))
    query = query.order_by(Resume.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total


def get_resume(db: Session, user: User, resume_id: int) -> Resume | None:
    return db.query(Resume).filter(Resume.user_id == user.id, Resume.id == resume_id).first()


def download_resume(resume: Resume) -> tuple[bytes, str]:
    path = Path(resume.storage_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")
    return path.read_bytes(), resume.content_type


def delete_resume(db: Session, user: User, resume_id: int) -> None:
    resume = get_resume(db, user, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    path = Path(resume.storage_path)
    if path.exists():
        path.unlink()

    if resume.is_active:
        fallback = db.query(Resume).filter(Resume.user_id == user.id, Resume.id != resume_id).order_by(Resume.created_at.desc()).first()
        if fallback is not None:
            fallback.is_active = True
            db.add(fallback)

    db.delete(resume)
    db.commit()


def set_active_resume(db: Session, user: User, resume_id: int) -> Resume:
    resume = get_resume(db, user, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    current = db.query(Resume).filter(Resume.user_id == user.id, Resume.is_active.is_(True)).first()
    if current is not None and current.id != resume.id:
        current.is_active = False
        db.add(current)

    resume.is_active = True
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume
