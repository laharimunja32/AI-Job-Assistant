from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DashboardJobItem(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    skills: list[str] | None = None
    experience: str | None = None
    employment_type: str | None = None
    work_mode: str | None = None
    salary: str | None = None
    apply_url: str | None = None
    source: str | None = None
    posted_date: datetime | None = None
    status: str | None = None
    tags: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    match_score: int | None = None
    match_category: str | None = None
    matched_skills: list[str] = Field(default_factory=list)


class DashboardJobListResponse(BaseModel):
    items: list[DashboardJobItem]
    total: int
    page: int
    size: int


class DashboardWalkInItem(BaseModel):
    id: int
    company_name: str
    job_role: str
    venue: str | None = None
    city: str | None = None
    state: str | None = None
    walk_in_date: date | None = None
    walk_in_time: str | None = None
    registration_deadline: date | None = None
    eligibility: str | None = None
    skills: list[str] | None = None
    experience_required: str | None = None
    registration_url: str | None = None
    source: str | None = None
    event_status: str | None = None
    created_at: datetime | None = None


class DashboardWalkInListResponse(BaseModel):
    items: list[DashboardWalkInItem]
    total: int
    page: int
    size: int


class CityJobCount(BaseModel):
    city: str
    count: int


class JobsByCityResponse(BaseModel):
    cities: list[CityJobCount]
    total_cities: int


class RecentCompanyItem(BaseModel):
    company_name: str
    latest_job_at: datetime | None = None


class RecentCompaniesResponse(BaseModel):
    items: list[RecentCompanyItem]
    total: int
    page: int
    size: int


class ClosingSoonItem(BaseModel):
    type: str
    id: int | None = None
    title: str | None = None
    company: str | None = None
    company_name: str | None = None
    job_role: str | None = None
    venue: str | None = None
    city: str | None = None
    walk_in_date: date | None = None
    match_score: int | None = None
    match_category: str | None = None


class ClosingSoonResponse(BaseModel):
    items: list[ClosingSoonItem]
    total: int
    page: int
    size: int


class DashboardStatistics(BaseModel):
    total_active_jobs: int
    new_jobs_today: int
    walk_ins_today: int
    walk_ins_upcoming: int
    remote_jobs: int
    hybrid_jobs: int
    total_matches: int
    high_matches: int
    strong_matches: int
    average_match_score: float
    profile_completeness: float
    last_aggregation_at: datetime | None = None
    total_applications: int = 0
    draft_applications: int = 0
    ready_to_apply: int = 0
    applied_today: int = 0
    interviews: int = 0
    offers: int = 0
    rejections: int = 0
    favorites: int = 0
    browser_active_sessions: int = 0
    browser_navigation_success_rate: float = 100.0
    browser_last_activity: datetime | None = None
    browser_status: str = "healthy"
    forms_detected: int = 0
    fields_filled: int = 0
    manual_fields_remaining: int = 0
    average_fill_success_rate: float = 0.0
    successful_uploads: int = 0
    failed_uploads: int = 0
    resume_upload_count: int = 0
    cover_letter_upload_count: int = 0
    average_upload_time_ms: float = 0.0
    ready_to_submit: int = 0
    applications_under_review: int = 0
    submitted_today: int = 0
    validation_failures: int = 0
    average_readiness_score: float = 0.0
    upcoming_assessments: int = 0
    upcoming_interviews: int = 0
    unread_recruitment_emails: int = 0
    todays_deadlines: int = 0
    interview_preparations: int = 0
    interview_practice_sessions: int = 0
    interview_questions_answered: int = 0
    average_interview_readiness: float | None = None
    average_interview_confidence: float | None = None


class ProfileSummary(BaseModel):
    has_profile: bool
    skills_count: int = 0
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    education_count: int = 0
    certifications_count: int = 0
    profile_completeness: float = 0.0


class RecentTailoredResumeItem(BaseModel):
    id: int
    job_id: int
    resume_version: int
    ats_score: float | None = None
    generated_at: datetime | None = None
    status: str


class ResumeGenerationHistoryItem(BaseModel):
    id: int
    tailored_resume_id: int | None = None
    job_id: int
    status: str
    message: str | None = None
    ats_score: float | None = None
    generated_at: datetime | None = None
    created_at: datetime


class RecentCoverLetterItem(BaseModel):
    id: int
    job_id: int
    company_name: str | None = None
    cover_letter_version: int
    quality_score: float | None = None
    generated_at: datetime | None = None
    status: str


class CoverLetterGenerationHistoryItem(BaseModel):
    id: int
    generated_cover_letter_id: int | None = None
    job_id: int
    company_name: str | None = None
    status: str
    message: str | None = None
    quality_score: float | None = None
    created_at: datetime


class RecentCoverLetterTemplateItem(BaseModel):
    id: int
    name: str
    is_default: bool
    version: int
    updated_at: datetime


class CoverLetterStatistics(BaseModel):
    total_generated: int
    queued_or_processing: int
    failed: int
    average_quality_score: float | None = None
    cache_hits: int


class TopicScoreItem(BaseModel):
    topic: str
    score: float


class RecentInterviewItem(BaseModel):
    id: int
    preparation_id: int
    job_id: int
    company_name: str | None = None
    job_title: str | None = None
    overall_score: float | None = None
    readiness_score: float | None = None
    questions_answered: int
    duration_seconds: int | None = None
    completed_at: datetime | None = None


class InterviewStatisticsDashboard(BaseModel):
    total_preparations: int
    practice_sessions: int
    questions_answered: int
    average_readiness: float | None = None
    average_confidence: float | None = None
    strongest_topics: list[TopicScoreItem] = Field(default_factory=list)
    weakest_topics: list[TopicScoreItem] = Field(default_factory=list)


class RecruitmentTimelineDigestItem(BaseModel):
    id: int
    application_id: int
    event_type: str
    title: str
    event_time: datetime


class RecruitmentSummary(BaseModel):
    upcoming_assessments: int
    upcoming_interviews: int
    offers: int
    rejections: int
    unread_recruitment_emails: int
    todays_deadlines: int
    recent_timeline_events: list[RecruitmentTimelineDigestItem] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    new_jobs: DashboardJobListResponse
    new_jobs_today: DashboardJobListResponse
    high_match_jobs: DashboardJobListResponse
    recommended_jobs: DashboardJobListResponse
    walk_ins: DashboardWalkInListResponse
    todays_walk_ins: DashboardWalkInListResponse
    upcoming_walk_ins: DashboardWalkInListResponse
    remote_jobs: DashboardJobListResponse
    hybrid_jobs: DashboardJobListResponse
    jobs_by_city: JobsByCityResponse
    recent_companies: RecentCompaniesResponse
    closing_soon: ClosingSoonResponse
    recently_updated_jobs: DashboardJobListResponse
    statistics: DashboardStatistics
    profile_summary: ProfileSummary
    recent_tailored_resumes: list[RecentTailoredResumeItem] = Field(default_factory=list)
    resume_generation_history: list[ResumeGenerationHistoryItem] = Field(default_factory=list)
    resume_ats_average: float | None = None
    resume_improvement_suggestions: list[str] = Field(default_factory=list)
    recent_cover_letters: list[RecentCoverLetterItem] = Field(default_factory=list)
    cover_letter_generation_history: list[CoverLetterGenerationHistoryItem] = Field(default_factory=list)
    recent_cover_letter_templates: list[RecentCoverLetterTemplateItem] = Field(default_factory=list)
    cover_letter_statistics: CoverLetterStatistics
    recruitment_summary: RecruitmentSummary
    recent_interviews: list[RecentInterviewItem] = Field(default_factory=list)
    interview_statistics: InterviewStatisticsDashboard


class RefreshResponse(BaseModel):
    matches_computed: int
    high_matches: int
    average_score: float


class AggregationRunRead(BaseModel):
    id: int
    run_type: str
    status: str
    providers_attempted: int
    providers_succeeded: int
    providers_failed: int
    jobs_created: int
    jobs_updated: int
    jobs_expired: int
    walk_ins_created: int
    walk_ins_updated: int
    duplicates_skipped: int
    errors: list[dict] = Field(default_factory=list)
    duration_seconds: float | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AggregationHistoryResponse(BaseModel):
    items: list[AggregationRunRead]
    total: int
    page: int
    size: int


class AggregationStatsResponse(BaseModel):
    jobs_created: int
    jobs_updated: int
    jobs_expired: int
    walk_ins_created: int
    walk_ins_updated: int
    duplicates_skipped: int
    providers_attempted: int
    providers_succeeded: int
    providers_failed: int
    errors: list[dict] = Field(default_factory=list)


class NotificationCandidateJob(BaseModel):
    job_id: int | None = None
    title: str | None = None
    company: str | None = None
    score: int | None = None
    category: str | None = None
    matched_at: datetime | None = None
    apply_url: str | None = None
    work_mode: str | None = None


class NotificationCandidateWalkIn(BaseModel):
    walk_in_id: int | None = None
    company_name: str | None = None
    job_role: str | None = None
    city: str | None = None
    walk_in_date: date | None = None
    event_status: str | None = None


class NotificationClosingSoon(BaseModel):
    type: str
    id: int | None = None
    title: str | None = None
    company: str | None = None
    deadline: date | None = None
    city: str | None = None


class NotificationCandidatesResponse(BaseModel):
    newly_matched_jobs: list[NotificationCandidateJob]
    newly_added_walk_ins: list[NotificationCandidateWalkIn]
    jobs_closing_soon: list[NotificationClosingSoon]
    high_priority_opportunities: list[NotificationCandidateJob]
