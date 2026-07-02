from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InterviewPreparationCreate(BaseModel):
    application_id: int | None = None


class InterviewPreparationGenerateResponse(BaseModel):
    preparation_id: int
    status: str
    cached: bool
    message: str


class InterviewQuestionRead(BaseModel):
    id: int
    preparation_id: int
    category: str
    question_text: str
    difficulty: str
    follow_up_questions: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewPreparationRead(BaseModel):
    id: int
    user_id: int
    job_id: int
    application_id: int | None = None
    tailored_resume_id: int | None = None
    cover_letter_id: int | None = None
    preparation_version: int
    status: str
    readiness_score: float | None = None
    confidence_score: float | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    behavioral_score: float | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    star_examples: list[dict[str, Any]] = Field(default_factory=list)
    recommended_topics: list[str] = Field(default_factory=list)
    important_topics: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    practice_recommendations: list[str] = Field(default_factory=list)
    estimated_duration_minutes: int | None = None
    analysis: dict[str, Any] = Field(default_factory=dict)
    completed: bool = False
    generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    questions: list[InterviewQuestionRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class InterviewAnswerCreate(BaseModel):
    answer_text: str
    time_spent_seconds: int | None = None


class InterviewAnswerRead(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_text: str | None = None
    ai_score: float | None = None
    feedback: str | None = None
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    time_spent_seconds: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionProgress(BaseModel):
    current_index: int
    total_questions: int
    questions_answered: int
    percent_complete: float


class InterviewSessionRead(BaseModel):
    id: int
    preparation_id: int
    user_id: int
    job_id: int
    status: str
    current_question_index: int
    total_questions: int
    questions_answered: int
    duration_seconds: int | None = None
    completed: bool
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionStartResponse(BaseModel):
    session: InterviewSessionRead
    current_question: InterviewQuestionRead
    progress: InterviewSessionProgress


class InterviewAnswerSubmitResponse(BaseModel):
    answer: InterviewAnswerRead
    session: InterviewSessionRead
    next_question: InterviewQuestionRead | None = None
    progress: InterviewSessionProgress


class InterviewFeedbackRead(BaseModel):
    id: int
    session_id: int
    preparation_id: int
    overall_score: float | None = None
    readiness_score: float | None = None
    confidence_score: float | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    behavioral_score: float | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    important_topics: list[str] = Field(default_factory=list)
    practice_recommendations: list[str] = Field(default_factory=list)
    recommended_resources: list[str] = Field(default_factory=list)
    topics_to_improve: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionFinishResponse(BaseModel):
    session: InterviewSessionRead
    feedback: InterviewFeedbackRead


class InterviewHistoryItem(BaseModel):
    id: int
    preparation_id: int
    job_id: int
    company_name: str | None = None
    job_title: str | None = None
    overall_score: float | None = None
    readiness_score: float | None = None
    confidence_score: float | None = None
    questions_answered: int
    duration_seconds: int | None = None
    completed_at: datetime | None = None


class InterviewHistoryResponse(BaseModel):
    items: list[InterviewHistoryItem]
    total: int
    page: int
    size: int


class TopicScoreItem(BaseModel):
    topic: str
    score: float


class InterviewStatistics(BaseModel):
    total_preparations: int
    completed_preparations: int
    practice_sessions: int
    questions_answered: int
    average_readiness: float | None = None
    average_confidence: float | None = None
    strongest_topics: list[TopicScoreItem] = Field(default_factory=list)
    weakest_topics: list[TopicScoreItem] = Field(default_factory=list)
    category_breakdown: dict[str, float] = Field(default_factory=dict)
