from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.db.models.application import Application
from app.db.models.browser_session import BrowserSession
from app.db.models.submission_review import SubmissionReviewAudit
from app.db.models.cover_letter import GeneratedCoverLetter
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import TailoredResume
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.browser import (
    BrowserOpenApplicationRequest,
    BrowserSessionCreate,
    BrowserSessionListResponse,
    BrowserSessionRead,
    BrowserSessionRestartRequest,
    BrowserStatusSummary,
    BrowserReviewConfirmRequest,
    BrowserReviewConfirmResponse,
    BrowserReviewReport,
    FormDetectionResponse,
    FormFillRequest,
    FormFillResponse,
    SubmissionAuditHistoryResponse,
    SubmissionValidationReport,
    UploadDetectionResponse,
    UploadExecutionRequest,
    UploadRetryRequest,
    UploadStatusResponse,
)
from app.services.browser.auto_fill_service import AutoFillService
from app.services.browser.document_upload_service import DocumentUploadService
from app.services.browser.form_detection_service import FormDetectionService
from app.services.browser.navigation_service import NavigationService
from app.services.browser.upload_detection_service import UploadDetectionService
from app.services.browser.review_service import ReviewInputs, ReviewService
from app.services.browser.submission_audit_service import SubmissionAuditService
from app.services.browser.submission_validation_service import SubmissionValidationService

router = APIRouter(prefix="/browser", tags=["browser-automation"])


def _to_read_model(session: BrowserSession) -> BrowserSessionRead:
    return BrowserSessionRead(
        session_id=session.session_id,
        user_id=session.user_id,
        application_id=session.application_id,
        browser_type=session.browser_type,
        status=session.status,
        current_url=session.current_url,
        started_time=session.started_time,
        last_activity=session.last_activity,
        screenshot_path=session.screenshot_path,
        error_message=session.error_message,
    )


def _get_manager(request: Request):
    manager = getattr(request.app.state, "browser_manager", None)
    if manager is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Browser manager unavailable")
    return manager


def _resolve_session(db: Session, user: User, session_id: str) -> BrowserSession:
    session = db.query(BrowserSession).filter(BrowserSession.session_id == session_id, BrowserSession.user_id == user.id).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser session not found")
    return session


@router.post("/session", response_model=BrowserSessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: BrowserSessionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserSessionRead:
    manager = _get_manager(request)
    browser_type = payload.browser_type or settings.playwright_browser
    try:
        record = manager.create_session(db, user_id=current_user.id, browser_type=browser_type, application_id=payload.application_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_read_model(record)


@router.post("/open/{application_id}", response_model=BrowserSessionRead)
def open_application(
    application_id: int,
    payload: BrowserOpenApplicationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserSessionRead:
    manager = _get_manager(request)
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == current_user.id, Application.is_deleted.is_(False))
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if not application.apply_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application apply URL is empty")

    session = _resolve_session(db, current_user, payload.session_id) if payload.session_id else None
    if session is None:
        try:
            session = manager.create_session(
                db,
                user_id=current_user.id,
                browser_type=payload.browser_type or settings.playwright_browser,
                application_id=application.id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    navigation = NavigationService(manager)
    try:
        metadata = navigation.open_apply_url(session, application.apply_url)
        session.current_url = metadata.final_url
        session.status = "active"
        session.application_id = application.id
        session.last_activity = datetime.utcnow()
        session.error_message = None
    except Exception as exc:
        screenshot = manager.capture_screenshot(session.session_id)
        session.status = "failed"
        session.error_message = str(exc)
        session.screenshot_path = screenshot
        session.last_activity = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    db.add(session)
    db.commit()
    db.refresh(session)
    output = _to_read_model(session)
    output.metadata = metadata
    return output


@router.get("/session/{session_id}", response_model=BrowserSessionRead)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserSessionRead:
    return _to_read_model(_resolve_session(db, current_user, session_id))


@router.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def close_session(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    session = _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    manager.close_session(session.session_id, db=db, status="closed")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/sessions", response_model=BrowserSessionListResponse)
def list_sessions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserSessionListResponse:
    manager = _get_manager(request)
    manager.cleanup_idle_sessions(db)
    items = (
        db.query(BrowserSession)
        .filter(BrowserSession.user_id == current_user.id)
        .order_by(BrowserSession.last_activity.desc())
        .all()
    )
    return BrowserSessionListResponse(items=[_to_read_model(item) for item in items], total=len(items))


@router.post("/session/{session_id}/restart", response_model=BrowserSessionRead)
def restart_session(
    session_id: str,
    payload: BrowserSessionRestartRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserSessionRead:
    manager = _get_manager(request)
    session = _resolve_session(db, current_user, session_id)
    try:
        restarted = manager.restart_session(db, session, browser_type=payload.browser_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_read_model(restarted)


@router.get("/status", response_model=BrowserStatusSummary)
def browser_status(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserStatusSummary:
    manager = _get_manager(request)
    summary = manager.status_summary(db, current_user.id)
    return BrowserStatusSummary(**summary)


@router.post("/forms/detect/{session_id}", response_model=FormDetectionResponse)
def detect_form_fields(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FormDetectionResponse:
    session = _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    page = manager.get_page(session.session_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser page not found for session")

    detection_service = FormDetectionService()
    fields = detection_service.detect_fields(page)
    response = FormDetectionResponse(
        session_id=session.session_id,
        page_url=page.url if hasattr(page, "url") else session.current_url,
        fields=fields,
        total_fields=len(fields),
    )
    manager.cache_form_detection(session.session_id, response)
    manager.touch(db, session, current_url=response.page_url)
    return response


@router.post("/forms/fill/{session_id}", response_model=FormFillResponse)
def auto_fill_form_fields(
    session_id: str,
    payload: FormFillRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FormFillResponse:
    session = _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    page = manager.get_page(session.session_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser page not found for session")

    detection = manager.get_form_detection(session.session_id)
    if detection is None:
        detection_service = FormDetectionService()
        fields = detection_service.detect_fields(page)
    else:
        fields = detection.fields

    auto_fill = AutoFillService()
    user_data = auto_fill.build_user_data(db, current_user)
    report = auto_fill.fill_fields(
        page=page,
        session_id=session.session_id,
        detected_fields=fields,
        user_data=user_data,
        overrides=payload.overrides,
        traverse_steps=payload.traverse_steps,
    )
    manager.cache_form_report(session.session_id, report)
    manager.touch(db, session, current_url=report.page_url)
    return report


@router.get("/forms/report/{session_id}", response_model=FormFillResponse)
def get_form_fill_report(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FormFillResponse:
    _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    report = manager.get_form_report(session_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No form report available for this session")
    return report


def _resolve_application(db: Session, user: User, application_id: int) -> Application:
    application = (
        db.query(Application)
        .filter(Application.id == application_id, Application.user_id == user.id, Application.is_deleted.is_(False))
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


def _resolve_session_application(db: Session, user: User, session: BrowserSession) -> Application:
    if session.application_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not linked to an application")
    return _resolve_application(db, user, session.application_id)


def _validate_document_ownership(db: Session, user: User, application: Application) -> None:
    if application.selected_resume_id:
        resume = db.query(Resume).filter(Resume.id == application.selected_resume_id, Resume.user_id == user.id).first()
        if resume is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Selected resume does not belong to current user")
    if application.selected_tailored_resume_id:
        tailored = (
            db.query(TailoredResume)
            .filter(TailoredResume.id == application.selected_tailored_resume_id, TailoredResume.user_id == user.id)
            .first()
        )
        if tailored is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Selected tailored resume does not belong to current user")
    if application.selected_cover_letter_id:
        cover = (
            db.query(GeneratedCoverLetter)
            .filter(GeneratedCoverLetter.id == application.selected_cover_letter_id, GeneratedCoverLetter.user_id == user.id)
            .first()
        )
        if cover is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Selected cover letter does not belong to current user")


@router.post("/uploads/detect/{session_id}", response_model=UploadDetectionResponse)
def detect_upload_fields(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadDetectionResponse:
    session = _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    page = manager.get_page(session.session_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser page not found for session")
    service = UploadDetectionService()
    fields = service.detect_fields(page)
    response = UploadDetectionResponse(
        session_id=session.session_id,
        page_url=page.url if hasattr(page, "url") else session.current_url,
        fields=fields,
        total_fields=len(fields),
    )
    manager.cache_upload_detection(session.session_id, response)
    manager.touch(db, session, current_url=response.page_url)
    return response


def _run_upload(
    session_id: str,
    payload: UploadExecutionRequest,
    request: Request,
    db: Session,
    current_user: User,
    include_resume: bool,
    include_cover_letter: bool,
) -> UploadStatusResponse:
    session = _resolve_session(db, current_user, session_id)
    application = _resolve_application(db, current_user, payload.application_id)
    _validate_document_ownership(db, current_user, application)
    manager = _get_manager(request)
    page = manager.get_page(session.session_id)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Browser page not found for session")

    detection = None if payload.force_redetect else manager.get_upload_detection(session.session_id)
    if detection is None:
        detection = UploadDetectionResponse(
            session_id=session.session_id,
            page_url=page.url if hasattr(page, "url") else session.current_url,
            fields=UploadDetectionService().detect_fields(page),
            total_fields=0,
        )
        detection.total_fields = len(detection.fields)
        manager.cache_upload_detection(session.session_id, detection)

    upload_service = DocumentUploadService()
    report = upload_service.upload_documents(
        db=db,
        page=page,
        session=session,
        user=current_user,
        application=application,
        detected_fields=detection.fields,
        include_resume=include_resume,
        include_cover_letter=include_cover_letter,
        use_tailored_resume=payload.use_tailored_resume,
    )
    manager.cache_upload_report(session.session_id, report)
    manager.touch(db, session, current_url=page.url if hasattr(page, "url") else session.current_url)
    return report


@router.post("/uploads/resume/{session_id}", response_model=UploadStatusResponse)
def upload_resume(
    session_id: str,
    payload: UploadExecutionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadStatusResponse:
    return _run_upload(session_id, payload, request, db, current_user, include_resume=True, include_cover_letter=False)


@router.post("/uploads/cover-letter/{session_id}", response_model=UploadStatusResponse)
def upload_cover_letter(
    session_id: str,
    payload: UploadExecutionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadStatusResponse:
    return _run_upload(session_id, payload, request, db, current_user, include_resume=False, include_cover_letter=True)


@router.post("/uploads/all/{session_id}", response_model=UploadStatusResponse)
def upload_all_documents(
    session_id: str,
    payload: UploadExecutionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadStatusResponse:
    return _run_upload(session_id, payload, request, db, current_user, include_resume=True, include_cover_letter=True)


@router.get("/uploads/status/{session_id}", response_model=UploadStatusResponse)
def upload_status(
    session_id: str,
    application_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadStatusResponse:
    session = _resolve_session(db, current_user, session_id)
    manager = _get_manager(request)
    cached = manager.get_upload_report(session.session_id)
    if cached is not None and cached.application_id == application_id:
        return cached
    return DocumentUploadService().build_status(db, session, application_id)


@router.post("/uploads/retry/{session_id}", response_model=UploadStatusResponse)
def retry_upload(
    session_id: str,
    payload: UploadRetryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadStatusResponse:
    request_payload = UploadExecutionRequest(
        application_id=payload.application_id,
        use_tailored_resume=True,
        force_redetect=False,
    )
    return _run_upload(
        session_id=session_id,
        payload=request_payload,
        request=request,
        db=db,
        current_user=current_user,
        include_resume=payload.include_resume,
        include_cover_letter=payload.include_cover_letter,
    )


@router.get("/review/{session_id}", response_model=BrowserReviewReport)
def get_review(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserReviewReport:
    session = _resolve_session(db, current_user, session_id)
    application = _resolve_session_application(db, current_user, session)
    manager = _get_manager(request)

    detection = manager.get_form_detection(session_id)
    form_report = manager.get_form_report(session_id)
    upload_report = manager.get_upload_report(session_id)
    validation = SubmissionValidationService().validate(
        session_active=session.status == "active",
        has_resume_selection=application.selected_resume_id is not None or application.selected_tailored_resume_id is not None,
        has_cover_letter_selection=application.selected_cover_letter_id is not None,
        cover_letter_required=bool(detection and any("cover" in (field.field_type or "").lower() and field.required for field in detection.fields)),
        detection=detection,
        upload_status=upload_report,
    )
    return ReviewService().analyze(
        session_id=session_id,
        application_id=application.id,
        review_inputs=ReviewInputs(
            form_report=form_report,
            upload_report=upload_report,
            validation_report=validation,
            browser_status=session.status,
            current_url=session.current_url,
        ),
    )


@router.post("/review/validate/{session_id}", response_model=SubmissionValidationReport)
def validate_review(
    session_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SubmissionValidationReport:
    session = _resolve_session(db, current_user, session_id)
    application = _resolve_session_application(db, current_user, session)
    manager = _get_manager(request)
    detection = manager.get_form_detection(session_id)
    upload_report = manager.get_upload_report(session_id)
    return SubmissionValidationService().validate(
        session_active=session.status == "active",
        has_resume_selection=application.selected_resume_id is not None or application.selected_tailored_resume_id is not None,
        has_cover_letter_selection=application.selected_cover_letter_id is not None,
        cover_letter_required=bool(detection and any("cover" in (field.field_type or "").lower() and field.required for field in detection.fields)),
        detection=detection,
        upload_status=upload_report,
    )


@router.post("/review/confirm/{session_id}", response_model=BrowserReviewConfirmResponse)
def confirm_review(
    session_id: str,
    payload: BrowserReviewConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BrowserReviewConfirmResponse:
    if not payload.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Explicit user confirmation is required")
    session = _resolve_session(db, current_user, session_id)
    application = _resolve_session_application(db, current_user, session)
    manager = _get_manager(request)
    detection = manager.get_form_detection(session_id)
    form_report = manager.get_form_report(session_id)
    upload_report = manager.get_upload_report(session_id)
    validation = SubmissionValidationService().validate(
        session_active=session.status == "active",
        has_resume_selection=application.selected_resume_id is not None or application.selected_tailored_resume_id is not None,
        has_cover_letter_selection=application.selected_cover_letter_id is not None,
        cover_letter_required=bool(detection and any("cover" in (field.field_type or "").lower() and field.required for field in detection.fields)),
        detection=detection,
        upload_status=upload_report,
    )
    review = ReviewService().analyze(
        session_id=session_id,
        application_id=application.id,
        review_inputs=ReviewInputs(
            form_report=form_report,
            upload_report=upload_report,
            validation_report=validation,
            browser_status=session.status,
            current_url=session.current_url,
        ),
    )
    return SubmissionAuditService().record(
        db=db,
        user=current_user,
        application=application,
        browser_session=session,
        review_report=review,
        validation_report=validation,
        payload=payload,
    )


@router.get("/review/history/{application_id}", response_model=SubmissionAuditHistoryResponse)
def review_history(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SubmissionAuditHistoryResponse:
    _resolve_application(db, current_user, application_id)
    rows = (
        db.query(SubmissionReviewAudit)
        .filter(SubmissionReviewAudit.application_id == application_id, SubmissionReviewAudit.user_id == current_user.id)
        .order_by(SubmissionReviewAudit.created_at.desc())
        .all()
    )
    return SubmissionAuditHistoryResponse(items=rows, total=len(rows))
