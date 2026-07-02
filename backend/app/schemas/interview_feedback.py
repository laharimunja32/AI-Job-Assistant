from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InterviewFeedbackEvaluateRequest(BaseModel):
    session_id: int


class QuestionReviewRead(BaseModel):
    question_id: int
    question_text: str
    category: str
    difficulty: str
    answer_text: str | None = None
    ai_score: float | None = None
    feedback: str | None = None
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    time_spent_seconds: int | None = None


class InterviewFeedbackDetailRead(BaseModel):
    id: int
    session_id: int
    preparation_id: int
    job_id: int | None = None
    company_name: str | None = None
    job_title: str | None = None
    overall_score: float | None = None
    readiness_score: float | None = None
    confidence_score: float | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    behavioral_score: float | None = None
    grammar_score: float | None = None
    clarity_score: float | None = None
    problem_solving_score: float | None = None
    summary_feedback: str | None = None
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    important_topics: list[str] = Field(default_factory=list)
    practice_recommendations: list[str] = Field(default_factory=list)
    recommended_resources: list[str] = Field(default_factory=list)
    topics_to_improve: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, Any] = Field(default_factory=dict)
    question_reviews: list[QuestionReviewRead] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewFeedbackHistoryItem(BaseModel):
    id: int
    session_id: int
    preparation_id: int
    job_id: int | None = None
    company_name: str | None = None
    job_title: str | None = None
    overall_score: float | None = None
    readiness_score: float | None = None
    confidence_score: float | None = None
    technical_score: float | None = None
    communication_score: float | None = None
    grammar_score: float | None = None
    clarity_score: float | None = None
    problem_solving_score: float | None = None
    created_at: datetime


class InterviewFeedbackHistoryResponse(BaseModel):
    items: list[InterviewFeedbackHistoryItem]
    total: int
    page: int
    size: int


class ScoreTrendPoint(BaseModel):
    feedback_id: int
    date: datetime
    overall_score: float | None = None


class SkillDistributionPoint(BaseModel):
    skill: str
    score: float


class InterviewFeedbackProgressRead(BaseModel):
    average_score: float | None = None
    best_score: float | None = None
    latest_score: float | None = None
    completed_interviews: int
    strongest_skill: str | None = None
    weakest_skill: str | None = None
    score_trend: list[ScoreTrendPoint] = Field(default_factory=list)
    skill_distribution: list[SkillDistributionPoint] = Field(default_factory=list)
    performance_breakdown: dict[str, float] = Field(default_factory=dict)
