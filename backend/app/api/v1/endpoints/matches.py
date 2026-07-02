from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.match import MatchHistoryResponse, MatchRead
from app.services.jobs.match_service import JobMatchService

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/jobs/{job_id}", response_model=MatchRead, summary="Match the current user with a specific job")
def match_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> MatchRead:
    service = JobMatchService(db=db)
    return service.match_job(job_id, current_user)


@router.post("/jobs", response_model=list[MatchRead], summary="Match the current user against all jobs")
def match_all_jobs(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> list[MatchRead]:
    service = JobMatchService(db=db)
    return [service.match_job(job.id, current_user) for job in db.query(__import__("app.db.models.job", fromlist=["Job"]).Job).filter(__import__("app.db.models.job", fromlist=["Job"]).Job.status == "active").all()]


@router.get("", response_model=MatchHistoryResponse, summary="Get persisted match history")
def get_match_history(
    min_score: int | None = Query(default=None, ge=0, le=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MatchHistoryResponse:
    service = JobMatchService(db=db)
    return service.get_match_history(current_user, min_score=min_score, page=page, size=size)


@router.post("/{match_id}/recalculate", response_model=MatchRead, summary="Recalculate a stored match")
def recalculate_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> MatchRead:
    service = JobMatchService(db=db)
    try:
        return service.recalculate_match(match_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a persisted match")
def delete_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> Response:
    match = db.query(__import__("app.services.jobs.match_service", fromlist=["JobMatch"]).JobMatch).filter(__import__("app.services.jobs.match_service", fromlist=["JobMatch"]).JobMatch.id == match_id, __import__("app.services.jobs.match_service", fromlist=["JobMatch"]).JobMatch.user_id == current_user.id).first()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    db.delete(match)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
