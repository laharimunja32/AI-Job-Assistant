export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  role: 'user' | 'admin';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface Job {
  id: number;
  title: string;
  company: string | null;
  description: string | null;
  skills: string[] | null;
  experience: string | null;
  education: string[] | null;
  employment_type: string | null;
  work_mode: string | null;
  location: string | null;
  salary: string | null;
  apply_url: string | null;
  source: string | null;
  posted_date: string | null;
  last_updated: string | null;
  status: string | null;
  tags: string[] | null;
  external_id: string | null;
  created_at: string;
  updated_at: string;
  match_score?: number | null;
  match_category?: string | null;
  matched_skills?: string[];
}

export interface DashboardJobItem extends Omit<Job, 'education' | 'last_updated' | 'external_id' | 'created_at' | 'updated_at'> {
  created_at?: string | null;
  updated_at?: string | null;
}

export interface WalkIn {
  id: number;
  company_name: string;
  job_role: string;
  job_description?: string | null;
  venue: string | null;
  city: string | null;
  state: string | null;
  walk_in_date: string | null;
  walk_in_time: string | null;
  registration_deadline: string | null;
  eligibility: string | null;
  degree?: string | null;
  branch?: string | null;
  passout_year?: string | null;
  skills: string[] | null;
  experience_required: string | null;
  documents_required?: string[] | null;
  contact_details?: string | null;
  registration_url: string | null;
  source: string | null;
  event_status: string;
  created_at: string;
  updated_at: string;
}

export interface DashboardWalkInItem {
  id: number;
  company_name: string;
  job_role: string;
  venue: string | null;
  city: string | null;
  state: string | null;
  walk_in_date: string | null;
  walk_in_time: string | null;
  registration_deadline: string | null;
  eligibility: string | null;
  skills: string[] | null;
  experience_required: string | null;
  registration_url: string | null;
  source: string | null;
  event_status: string | null;
  created_at: string | null;
}

export interface EducationItem {
  institution: string | null;
  degree: string | null;
  field: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
}

export interface CertificationItem {
  name: string | null;
  issuer: string | null;
  issued_date: string | null;
  expires_at: string | null;
}

export interface ProjectItem {
  name: string | null;
  description: string | null;
  url: string | null;
}

export interface WorkPreferences {
  remote: boolean | null;
  relocation: boolean | null;
  availability: string | null;
}

export interface Profile {
  id: number;
  user_id: number;
  email: string | null;
  full_name: string | null;
  phone: string | null;
  address: string | null;
  location: string | null;
  education: EducationItem[];
  skills: string[];
  certifications: CertificationItem[];
  projects: ProjectItem[];
  work_preferences: WorkPreferences | Record<string, unknown>;
  preferred_job_roles: string[];
  preferred_locations: string[];
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface Resume {
  id: number;
  user_id: number;
  filename: string;
  content_type: string;
  file_size: number;
  version: number;
  is_active: boolean;
  storage_path: string;
  metadata?: Record<string, unknown> | null;
  file_metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface Match {
  id: number | null;
  job_id: number | null;
  user_id: number | null;
  score: number;
  category: string;
  matched_skills: string[];
  missing_skills: string[];
  missing_certifications: string[];
  missing_technologies: string[];
  location_compatible: boolean;
  experience_compatible: boolean;
  reasoning: string;
  profile_improvements: string[];
  resume_improvements: string[];
  created_at: string | null;
}

export interface DashboardStatistics {
  total_active_jobs: number;
  new_jobs_today: number;
  walk_ins_today: number;
  walk_ins_upcoming: number;
  remote_jobs: number;
  hybrid_jobs: number;
  total_matches: number;
  high_matches: number;
  strong_matches: number;
  average_match_score: number;
  profile_completeness: number;
  last_aggregation_at: string | null;
  total_applications: number;
  draft_applications: number;
  ready_to_apply: number;
  applied_today: number;
  interviews: number;
  offers: number;
  rejections: number;
  favorites: number;
  browser_active_sessions: number;
  browser_navigation_success_rate: number;
  browser_last_activity: string | null;
  browser_status: string;
  forms_detected: number;
  fields_filled: number;
  manual_fields_remaining: number;
  average_fill_success_rate: number;
  successful_uploads: number;
  failed_uploads: number;
  resume_upload_count: number;
  cover_letter_upload_count: number;
  average_upload_time_ms: number;
  ready_to_submit: number;
  applications_under_review: number;
  submitted_today: number;
  validation_failures: number;
  average_readiness_score: number;
  upcoming_assessments: number;
  upcoming_interviews: number;
  unread_recruitment_emails: number;
  todays_deadlines: number;
  interview_preparations: number;
  interview_practice_sessions: number;
  interview_questions_answered: number;
  average_interview_readiness: number | null;
  average_interview_confidence: number | null;
}

export interface ProfileSummary {
  has_profile: boolean;
  skills_count: number;
  preferred_roles: string[];
  preferred_locations: string[];
  education_count: number;
  certifications_count: number;
  profile_completeness: number;
}

export interface ClosingSoonItem {
  type: string;
  id: number | null;
  title: string | null;
  company: string | null;
  company_name: string | null;
  job_role: string | null;
  venue: string | null;
  city: string | null;
  walk_in_date: string | null;
  match_score: number | null;
  match_category: string | null;
}

export interface CityJobCount {
  city: string;
  count: number;
}

export interface RecentCompanyItem {
  company_name: string;
  latest_job_at: string | null;
}

export interface DashboardResponse {
  new_jobs: PaginatedResponse<DashboardJobItem>;
  new_jobs_today: PaginatedResponse<DashboardJobItem>;
  high_match_jobs: PaginatedResponse<DashboardJobItem>;
  recommended_jobs: PaginatedResponse<DashboardJobItem>;
  walk_ins: PaginatedResponse<DashboardWalkInItem>;
  todays_walk_ins: PaginatedResponse<DashboardWalkInItem>;
  upcoming_walk_ins: PaginatedResponse<DashboardWalkInItem>;
  remote_jobs: PaginatedResponse<DashboardJobItem>;
  hybrid_jobs: PaginatedResponse<DashboardJobItem>;
  jobs_by_city: { cities: CityJobCount[]; total_cities: number };
  recent_companies: PaginatedResponse<RecentCompanyItem>;
  closing_soon: PaginatedResponse<ClosingSoonItem>;
  recently_updated_jobs: PaginatedResponse<DashboardJobItem>;
  statistics: DashboardStatistics;
  profile_summary: ProfileSummary;
  recent_tailored_resumes: RecentTailoredResumeItem[];
  resume_generation_history: ResumeGenerationHistoryItem[];
  resume_ats_average: number | null;
  resume_improvement_suggestions: string[];
  recent_cover_letters: RecentCoverLetterItem[];
  cover_letter_generation_history: CoverLetterGenerationHistoryItem[];
  recent_cover_letter_templates: RecentCoverLetterTemplateItem[];
  cover_letter_statistics: CoverLetterStatistics;
  recruitment_summary: RecruitmentSummary;
  recent_interviews: RecentInterviewItem[];
  interview_statistics: InterviewStatisticsDashboard;
}

export interface RecruitmentTimelineDigestItem {
  id: number;
  application_id: number;
  event_type: string;
  title: string;
  event_time: string;
}

export interface RecruitmentSummary {
  upcoming_assessments: number;
  upcoming_interviews: number;
  offers: number;
  rejections: number;
  unread_recruitment_emails: number;
  todays_deadlines: number;
  recent_timeline_events: RecruitmentTimelineDigestItem[];
}

export interface EmailEvent {
  id: number;
  user_id: number;
  application_id: number | null;
  provider: string | null;
  company_name: string | null;
  job_title: string | null;
  sender: string;
  subject: string;
  body_preview: string | null;
  received_time: string;
  event_type: string;
  interview_invitation: boolean;
  online_assessment: boolean;
  coding_test: boolean;
  hr_round: boolean;
  technical_round: boolean;
  offer: boolean;
  rejection: boolean;
  deadline: string | null;
  meeting_link: string | null;
  is_read: boolean;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type AssessmentStatus = 'Pending' | 'Scheduled' | 'Completed' | 'Expired' | 'Cancelled';
export interface Assessment {
  id: number;
  user_id: number;
  application_id: number | null;
  email_event_id: number | null;
  provider: string | null;
  assessment_url: string | null;
  assessment_type: string | null;
  duration_minutes: number | null;
  deadline: string | null;
  status: AssessmentStatus;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export type InterviewStatus = 'Scheduled' | 'Completed' | 'Cancelled' | 'Rescheduled';
export interface Interview {
  id: number;
  user_id: number;
  application_id: number | null;
  email_event_id: number | null;
  interview_type: string;
  interview_date: string | null;
  interview_time: string | null;
  time_zone: string | null;
  meeting_link: string | null;
  interviewer: string | null;
  notes: string | null;
  status: InterviewStatus;
  created_at: string;
  updated_at: string;
}

export interface TimelineEvent {
  id: number;
  user_id: number;
  application_id: number;
  event_type: string;
  title: string;
  description: string | null;
  source_type: string | null;
  source_id: number | null;
  event_time: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

export interface Reminder {
  id: number;
  user_id: number;
  application_id: number | null;
  timeline_event_id: number | null;
  title: string;
  note: string | null;
  due_at: string;
  status: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationHistory {
  id: number;
  user_id: number;
  application_id: number | null;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface RecentTailoredResumeItem {
  id: number;
  job_id: number;
  resume_version: number;
  ats_score: number | null;
  generated_at: string | null;
  status: string;
}

export interface ResumeGenerationHistoryItem {
  id: number;
  tailored_resume_id: number | null;
  job_id: number;
  status: string;
  message: string | null;
  ats_score: number | null;
  generated_at: string | null;
  created_at: string;
}

export interface CoverLetterTemplate {
  id: number;
  user_id: number;
  name: string;
  intro_style: string | null;
  closing_style: string | null;
  body_guidance: string | null;
  signature_block: string | null;
  is_default: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CoverLetterTemplatePayload {
  name: string;
  intro_style?: string | null;
  closing_style?: string | null;
  body_guidance?: string | null;
  signature_block?: string | null;
  is_default?: boolean;
}

export interface CoverLetterGenerateResponse {
  cover_letter_id: number;
  status: string;
  cached: boolean;
  message: string;
}

export interface GeneratedCoverLetter {
  id: number;
  user_id: number;
  job_id: number;
  company_name: string | null;
  template_id: number | null;
  resume_id: number | null;
  tailored_resume_id: number | null;
  match_id: number | null;
  cover_letter_version: number;
  status: string;
  download_formats: string[];
  analysis: {
    company_name: string;
    role: string;
    responsibilities: string[];
    required_skills: string[];
    preferred_skills: string[];
    company_values: string[];
    industry: string | null;
    keywords: string[];
  };
  sections: {
    introduction: string;
    role_interest: string;
    relevant_skills: string[];
    relevant_projects: string[];
    certifications: string[];
    closing_paragraph: string;
    professional_signature: string;
  };
  markdown_content: string | null;
  html_content: string | null;
  quality_score: number | null;
  generated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CoverLetterGenerationHistoryItem {
  id: number;
  generated_cover_letter_id: number | null;
  user_id: number;
  job_id: number;
  company_name: string | null;
  status: string;
  message: string | null;
  retry_count: number;
  quality_score: number | null;
  generated_at: string | null;
  created_at: string;
}

export interface RecentCoverLetterItem {
  id: number;
  job_id: number;
  company_name: string | null;
  cover_letter_version: number;
  quality_score: number | null;
  generated_at: string | null;
  status: string;
}

export interface RecentCoverLetterTemplateItem {
  id: number;
  name: string;
  is_default: boolean;
  version: number;
  updated_at: string;
}

export interface CoverLetterStatistics {
  total_generated: number;
  queued_or_processing: number;
  failed: number;
  average_quality_score: number | null;
  cache_hits: number;
}

export interface TailoredResumeGenerateResponse {
  tailored_resume_id: number;
  status: string;
  cached: boolean;
  message: string;
}

export interface TailoredResume {
  id: number;
  user_id: number;
  job_id: number;
  template_id: number | null;
  match_id: number | null;
  resume_version: number;
  status: string;
  generated_at: string | null;
  ats_score: number | null;
  analysis: {
    required_skills: string[];
    preferred_skills: string[];
    technologies: string[];
    experience: string | null;
    keywords: string[];
    responsibilities: string[];
    education: string[];
    certifications: string[];
  };
  improvements: {
    professional_summary: string;
    skills_ordering: string[];
    relevant_projects: string[];
    relevant_certifications: string[];
    achievements: string[];
    keyword_optimization: string[];
    ats_optimization: string[];
  };
  markdown_content: string | null;
  html_content: string | null;
  markdown_path: string | null;
  html_path: string | null;
  pdf_path: string | null;
  docx_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationCandidatesResponse {
  newly_matched_jobs: Array<{
    job_id: number | null;
    title: string | null;
    company: string | null;
    score: number | null;
    category: string | null;
    matched_at: string | null;
    apply_url: string | null;
    work_mode: string | null;
  }>;
  newly_added_walk_ins: Array<{
    walk_in_id: number | null;
    company_name: string | null;
    job_role: string | null;
    city: string | null;
    walk_in_date: string | null;
    event_status: string | null;
  }>;
  jobs_closing_soon: Array<{
    type: string;
    id: number | null;
    title: string | null;
    company: string | null;
    deadline: string | null;
    city: string | null;
  }>;
  high_priority_opportunities: Array<{
    job_id: number | null;
    title: string | null;
    company: string | null;
    score: number | null;
    category: string | null;
    matched_at: string | null;
    apply_url: string | null;
    work_mode: string | null;
  }>;
}

export interface AggregationRun {
  id: number;
  run_type: string;
  status: string;
  providers_attempted: number;
  providers_succeeded: number;
  providers_failed: number;
  jobs_created: number;
  jobs_updated: number;
  jobs_expired: number;
  walk_ins_created: number;
  walk_ins_updated: number;
  duplicates_skipped: number;
  errors: Record<string, unknown>[];
  duration_seconds: number | null;
  started_at: string;
  completed_at: string | null;
}

export type ApplicationStatus =
  | 'draft'
  | 'ready_to_apply'
  | 'applied'
  | 'assessment_received'
  | 'interview_scheduled'
  | 'technical_interview'
  | 'hr_interview'
  | 'offer_received'
  | 'offer_accepted'
  | 'offer_declined'
  | 'rejected'
  | 'withdrawn'
  | 'ready_to_submit'
  | 'review_required'
  | 'submitted'
  | 'submission_failed';

export interface Application {
  id: number;
  user_id: number;
  job_id: number;
  company_name: string;
  job_title: string;
  apply_url: string | null;
  status: ApplicationStatus;
  source: string | null;
  applied_date: string | null;
  selected_resume_id: number | null;
  selected_tailored_resume_id: number | null;
  selected_cover_letter_id: number | null;
  notes: string | null;
  tags: string[];
  priority: number;
  is_favorite: boolean;
  follow_up_date: string | null;
  created_at: string;
  updated_at: string;
  interview_prepared?: boolean;
  interview_completed?: boolean;
  interview_readiness_score?: number | null;
  interview_practice_sessions?: number;
  interview_preparation_id?: number | null;
}

export interface ApplicationHistoryItem {
  id: number;
  application_id: number;
  user_id: number;
  from_status: string | null;
  to_status: string;
  message: string | null;
  event_payload: Record<string, unknown>;
  created_at: string;
}

export type BrowserSessionStatus = 'active' | 'idle' | 'closed' | 'failed';
export type BrowserType = 'chromium' | 'edge' | 'firefox';

export interface BrowserPageMetadata {
  title: string | null;
  final_url: string | null;
  redirected: boolean;
  navigation_time_ms: number;
}

export interface BrowserSession {
  session_id: string;
  user_id: number;
  application_id: number | null;
  browser_type: BrowserType;
  status: BrowserSessionStatus;
  current_url: string | null;
  started_time: string;
  last_activity: string;
  screenshot_path: string | null;
  error_message: string | null;
  metadata?: BrowserPageMetadata | null;
}

export interface BrowserSessionListResponse {
  items: BrowserSession[];
  total: number;
}

export interface BrowserStatusSummary {
  active_sessions: number;
  last_browser_activity: string | null;
  navigation_success_rate: number;
  browser_status: string;
}

export interface DetectedFormField {
  field_id: string;
  field_type: string;
  selector: string;
  label: string | null;
  placeholder: string | null;
  input_name: string | null;
  input_type: string | null;
  required: boolean;
  confidence: number;
  value: string | null;
}

export interface FormDetectionResponse {
  session_id: string;
  page_url: string | null;
  fields: DetectedFormField[];
  total_fields: number;
  detected_at: string;
}

export interface FormFillFieldResult {
  field_id: string;
  field_type: string;
  selector: string;
  status: string;
  reason: string | null;
  value_preview: string | null;
}

export interface FormFillResponse {
  session_id: string;
  page_url: string | null;
  completion_percentage: number;
  filled_fields: FormFillFieldResult[];
  skipped_fields: FormFillFieldResult[];
  unknown_fields: FormFillFieldResult[];
  required_manual_input: FormFillFieldResult[];
  generated_at: string;
}

export interface UploadFieldDetection {
  field_id: string;
  field_type: string;
  selector: string;
  confidence: number;
  visible: boolean;
  upload_capability: string;
  input_type: string | null;
  trigger_selector?: string | null;
  nearby_text: string | null;
}

export interface UploadDetectionResponse {
  session_id: string;
  page_url: string | null;
  fields: UploadFieldDetection[];
  total_fields: number;
  detected_at: string;
}

export interface UploadValidationResult {
  accepted: boolean;
  accepted_file_types: string[];
  max_file_size_mb: number | null;
  multiple_allowed: boolean;
  messages: string[];
  validation_error: string | null;
}

export interface UploadFieldStatus {
  field_type: string;
  selector: string;
  status: string;
  document_type: string | null;
  filename: string | null;
  confidence: number;
  visible: boolean;
  upload_capability: string;
  validation: UploadValidationResult | null;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
}

export interface UploadStatusResponse {
  session_id: string;
  application_id: number;
  status: string;
  uploaded_fields: UploadFieldStatus[];
  failed_fields: UploadFieldStatus[];
  pending_fields: UploadFieldStatus[];
  generated_at: string;
}

export interface BrowserReviewSectionItem {
  key: string;
  label: string;
  value: string;
  detail: string | null;
}

export interface BrowserSessionReadiness {
  score: number;
  label: string;
  recommended_action: string;
}

export interface BrowserReviewReport {
  session_id: string;
  application_id: number;
  current_url: string | null;
  filled_fields: BrowserReviewSectionItem[];
  empty_required_fields: BrowserReviewSectionItem[];
  uploaded_documents: BrowserReviewSectionItem[];
  validation_errors: string[];
  optional_fields: BrowserReviewSectionItem[];
  page_warnings: string[];
  readiness: BrowserSessionReadiness;
  generated_at: string;
}

export interface SubmissionValidationReport {
  valid: boolean;
  checks: Record<string, boolean>;
  warnings: string[];
  errors: string[];
  validated_at: string;
}

export interface BrowserReviewConfirmResponse {
  application_id: number;
  session_id: string;
  result: string;
  status: string;
  confirmed: boolean;
  submission_attempted: boolean;
  timestamp: string;
}

export interface SubmissionAuditRead {
  id: number;
  application_id: number;
  session_id: string;
  review_time_seconds: number;
  readiness_score: number;
  validation_passed: boolean;
  validation_results: Record<string, unknown>;
  user_confirmation: boolean;
  submission_attempted: boolean;
  result: string;
  browser_session_status: string | null;
  current_url: string | null;
  warnings: string[];
  errors: string[];
  created_at: string;
}

export interface SubmissionAuditHistoryResponse {
  items: SubmissionAuditRead[];
  total: number;
}

export type Theme = 'light' | 'dark' | 'system';

export interface InterviewPreparationGenerateResponse {
  preparation_id: number;
  status: string;
  cached: boolean;
  message: string;
}

export interface InterviewQuestion {
  id: number;
  preparation_id: number;
  category: string;
  question_text: string;
  difficulty: string;
  follow_up_questions: string[];
  hints: string[];
  sort_order: number;
  created_at: string;
}

export interface InterviewPreparation {
  id: number;
  user_id: number;
  job_id: number;
  application_id: number | null;
  tailored_resume_id: number | null;
  cover_letter_id: number | null;
  preparation_version: number;
  status: string;
  readiness_score: number | null;
  confidence_score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  behavioral_score: number | null;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  star_examples: Array<Record<string, string>>;
  recommended_topics: string[];
  important_topics: string[];
  missing_skills: string[];
  practice_recommendations: string[];
  estimated_duration_minutes: number | null;
  analysis: Record<string, unknown>;
  completed: boolean;
  generated_at: string | null;
  created_at: string;
  updated_at: string;
  questions: InterviewQuestion[];
}

export interface InterviewAnswer {
  id: number;
  session_id: number;
  question_id: number;
  answer_text: string | null;
  ai_score: number | null;
  feedback: string | null;
  strengths: string[];
  improvements: string[];
  time_spent_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface InterviewSessionProgress {
  current_index: number;
  total_questions: number;
  questions_answered: number;
  percent_complete: number;
}

export interface InterviewSession {
  id: number;
  preparation_id: number;
  user_id: number;
  job_id: number;
  status: string;
  current_question_index: number;
  total_questions: number;
  questions_answered: number;
  duration_seconds: number | null;
  completed: boolean;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InterviewSessionStartResponse {
  session: InterviewSession;
  current_question: InterviewQuestion;
  progress: InterviewSessionProgress;
}

export interface InterviewAnswerSubmitResponse {
  answer: InterviewAnswer;
  session: InterviewSession;
  next_question: InterviewQuestion | null;
  progress: InterviewSessionProgress;
}

export interface InterviewFeedback {
  id: number;
  session_id: number;
  preparation_id: number;
  overall_score: number | null;
  readiness_score: number | null;
  confidence_score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  behavioral_score: number | null;
  strengths: string[];
  weaknesses: string[];
  improvement_suggestions: string[];
  missing_skills: string[];
  important_topics: string[];
  practice_recommendations: string[];
  recommended_resources: string[];
  topics_to_improve: string[];
  score_breakdown: Record<string, number>;
  created_at: string;
}

export interface InterviewSessionFinishResponse {
  session: InterviewSession;
  feedback: InterviewFeedback;
}

export interface InterviewHistoryItem {
  id: number;
  preparation_id: number;
  job_id: number;
  company_name: string | null;
  job_title: string | null;
  overall_score: number | null;
  readiness_score: number | null;
  confidence_score: number | null;
  questions_answered: number;
  duration_seconds: number | null;
  completed_at: string | null;
}

export interface TopicScoreItem {
  topic: string;
  score: number;
}

export interface InterviewStatistics {
  total_preparations: number;
  completed_preparations: number;
  practice_sessions: number;
  questions_answered: number;
  average_readiness: number | null;
  average_confidence: number | null;
  strongest_topics: TopicScoreItem[];
  weakest_topics: TopicScoreItem[];
  category_breakdown: Record<string, number>;
}

export interface RecentInterviewItem {
  id: number;
  preparation_id: number;
  job_id: number;
  company_name: string | null;
  job_title: string | null;
  overall_score: number | null;
  readiness_score: number | null;
  questions_answered: number;
  duration_seconds: number | null;
  completed_at: string | null;
}

export interface InterviewStatisticsDashboard {
  total_preparations: number;
  practice_sessions: number;
  questions_answered: number;
  average_readiness: number | null;
  average_confidence: number | null;
  strongest_topics: TopicScoreItem[];
  weakest_topics: TopicScoreItem[];
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
