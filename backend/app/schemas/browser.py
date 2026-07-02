from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

BROWSER_TYPES = {"chromium", "edge", "firefox"}
SESSION_STATUSES = {"active", "idle", "closed", "failed"}


class BrowserSessionCreate(BaseModel):
    browser_type: str = "chromium"
    application_id: int | None = None

    @field_validator("browser_type")
    @classmethod
    def validate_browser_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in BROWSER_TYPES:
            raise ValueError("Unsupported browser type")
        return normalized


class BrowserOpenApplicationRequest(BaseModel):
    session_id: str | None = None
    browser_type: str = "chromium"

    @field_validator("browser_type")
    @classmethod
    def validate_browser_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in BROWSER_TYPES:
            raise ValueError("Unsupported browser type")
        return normalized


class BrowserSessionRestartRequest(BaseModel):
    browser_type: str | None = None

    @field_validator("browser_type")
    @classmethod
    def validate_browser_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in BROWSER_TYPES:
            raise ValueError("Unsupported browser type")
        return normalized


class BrowserPageMetadata(BaseModel):
    title: str | None = None
    final_url: str | None = None
    redirected: bool = False
    navigation_time_ms: int


class BrowserSessionRead(BaseModel):
    session_id: str
    user_id: int
    application_id: int | None = None
    browser_type: str
    status: str
    current_url: str | None = None
    started_time: datetime
    last_activity: datetime
    screenshot_path: str | None = None
    error_message: str | None = None
    metadata: BrowserPageMetadata | None = None

    model_config = ConfigDict(from_attributes=True)


class BrowserSessionListResponse(BaseModel):
    items: list[BrowserSessionRead]
    total: int


class BrowserStatusSummary(BaseModel):
    active_sessions: int
    last_browser_activity: datetime | None = None
    navigation_success_rate: float
    browser_status: str


class BrowserEventLog(BaseModel):
    browser_launch_time_ms: int | None = None
    navigation_time_ms: int | None = None
    current_url: str | None = None
    browser_type: str
    session_duration_seconds: int | None = None
    error: str | None = None
    logged_at: datetime = Field(default_factory=datetime.utcnow)


class DetectedFormField(BaseModel):
    field_id: str
    field_type: str
    selector: str
    label: str | None = None
    placeholder: str | None = None
    input_name: str | None = None
    input_type: str | None = None
    required: bool = False
    confidence: float = 0.0
    value: str | None = None


class FormDetectionResponse(BaseModel):
    session_id: str
    page_url: str | None = None
    fields: list[DetectedFormField]
    total_fields: int
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class FormFillFieldResult(BaseModel):
    field_id: str
    field_type: str
    selector: str
    status: str
    reason: str | None = None
    value_preview: str | None = None


class FormFillRequest(BaseModel):
    overrides: dict[str, str] = Field(default_factory=dict)
    traverse_steps: bool = True


class FormFillResponse(BaseModel):
    session_id: str
    page_url: str | None = None
    completion_percentage: float
    filled_fields: list[FormFillFieldResult] = Field(default_factory=list)
    skipped_fields: list[FormFillFieldResult] = Field(default_factory=list)
    unknown_fields: list[FormFillFieldResult] = Field(default_factory=list)
    required_manual_input: list[FormFillFieldResult] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class UploadFieldDetection(BaseModel):
    field_id: str
    field_type: str
    selector: str
    confidence: float = 0.0
    visible: bool = True
    upload_capability: str = "standard"
    input_type: str | None = None
    trigger_selector: str | None = None
    nearby_text: str | None = None


class UploadDetectionResponse(BaseModel):
    session_id: str
    page_url: str | None = None
    fields: list[UploadFieldDetection] = Field(default_factory=list)
    total_fields: int = 0
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class UploadValidationResult(BaseModel):
    accepted: bool = True
    accepted_file_types: list[str] = Field(default_factory=list)
    max_file_size_mb: float | None = None
    multiple_allowed: bool = False
    messages: list[str] = Field(default_factory=list)
    validation_error: str | None = None


class UploadExecutionRequest(BaseModel):
    application_id: int
    use_tailored_resume: bool = True
    resume_id: int | None = None
    tailored_resume_id: int | None = None
    cover_letter_id: int | None = None
    force_redetect: bool = False


class UploadFieldStatus(BaseModel):
    field_type: str
    selector: str
    status: str
    document_type: str | None = None
    filename: str | None = None
    confidence: float = 0.0
    visible: bool = True
    upload_capability: str = "unknown"
    validation: UploadValidationResult | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None


class UploadStatusResponse(BaseModel):
    session_id: str
    application_id: int
    status: str
    uploaded_fields: list[UploadFieldStatus] = Field(default_factory=list)
    failed_fields: list[UploadFieldStatus] = Field(default_factory=list)
    pending_fields: list[UploadFieldStatus] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class UploadRetryRequest(BaseModel):
    application_id: int
    include_resume: bool = True
    include_cover_letter: bool = True


class BrowserReviewSectionItem(BaseModel):
    key: str
    label: str
    value: str
    detail: str | None = None


class BrowserSessionReadiness(BaseModel):
    score: int = Field(ge=0, le=100)
    label: str
    recommended_action: str


class BrowserReviewReport(BaseModel):
    session_id: str
    application_id: int
    current_url: str | None = None
    filled_fields: list[BrowserReviewSectionItem] = Field(default_factory=list)
    empty_required_fields: list[BrowserReviewSectionItem] = Field(default_factory=list)
    uploaded_documents: list[BrowserReviewSectionItem] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
    optional_fields: list[BrowserReviewSectionItem] = Field(default_factory=list)
    page_warnings: list[str] = Field(default_factory=list)
    readiness: BrowserSessionReadiness
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionValidationReport(BaseModel):
    valid: bool
    checks: dict[str, bool] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.utcnow)


class BrowserReviewConfirmRequest(BaseModel):
    confirmed: bool = True
    attempt_submission: bool = False
    review_time_seconds: int = 0


class BrowserReviewConfirmResponse(BaseModel):
    application_id: int
    session_id: str
    result: str
    status: str
    confirmed: bool
    submission_attempted: bool
    timestamp: datetime


class SubmissionAuditRead(BaseModel):
    id: int
    application_id: int
    session_id: str
    review_time_seconds: int
    readiness_score: float
    validation_passed: bool
    validation_results: dict = Field(default_factory=dict)
    user_confirmation: bool
    submission_attempted: bool
    result: str
    browser_session_status: str | None = None
    current_url: str | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionAuditHistoryResponse(BaseModel):
    items: list[SubmissionAuditRead]
    total: int
