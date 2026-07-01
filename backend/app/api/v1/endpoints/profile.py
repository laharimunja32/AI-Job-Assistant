from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.profile import ProfileCreateUpdate, ProfileRead
from app.services.profile_service import delete_profile, upsert_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get(
    "",
    response_model=ProfileRead,
    summary="Get the currently authenticated user profile",
    response_description="Current authenticated user profile",
)
def read_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProfileRead:
    profile = current_user.profile
    payload = {
        "id": profile.id if profile is not None else 0,
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": profile.phone if profile is not None else None,
        "address": profile.address if profile is not None else None,
        "location": profile.location if profile is not None else None,
        "education": profile.education or [] if profile is not None else [],
        "skills": profile.skills or [] if profile is not None else [],
        "certifications": profile.certifications or [] if profile is not None else [],
        "projects": profile.projects or [] if profile is not None else [],
        "work_preferences": profile.work_preferences or {} if profile is not None else {},
        "preferred_job_roles": profile.preferred_job_roles or [] if profile is not None else [],
        "preferred_locations": profile.preferred_locations or [] if profile is not None else [],
        "linkedin_url": profile.linkedin_url if profile is not None else None,
        "github_url": profile.github_url if profile is not None else None,
        "portfolio_url": profile.portfolio_url if profile is not None else None,
    }
    return payload


@router.put(
    "",
    response_model=ProfileRead,
    summary="Update the currently authenticated user profile",
    response_description="Updated current user profile",
)
def update_current_user(
    profile_update: ProfileCreateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProfileRead:
    if profile_update.model_dump(exclude_none=True):
        updated_profile = upsert_profile(db, current_user, profile_update)
        return {
            "id": updated_profile.id,
            "user_id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": updated_profile.phone,
            "address": updated_profile.address,
            "location": updated_profile.location,
            "education": updated_profile.education or [],
            "skills": updated_profile.skills or [],
            "certifications": updated_profile.certifications or [],
            "projects": updated_profile.projects or [],
            "work_preferences": updated_profile.work_preferences or {},
            "preferred_job_roles": updated_profile.preferred_job_roles or [],
            "preferred_locations": updated_profile.preferred_locations or [],
            "linkedin_url": updated_profile.linkedin_url,
            "github_url": updated_profile.github_url,
            "portfolio_url": updated_profile.portfolio_url,
        }

    return {
        "id": 0,
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "skills": [],
    }


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete the currently authenticated user profile",
    response_description="No content returned on successful deletion",
)
def delete_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    delete_profile(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
