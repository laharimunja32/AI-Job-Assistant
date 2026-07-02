from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.db.models.interview import InterviewAnswer, InterviewFeedback, InterviewQuestion, InterviewSession
from app.db.models.job import Job
from app.db.models.user import User
from app.services.interview_service import InterviewService


class InterviewFeedbackService:
    """Feedback and analytics facade over InterviewService."""

    def __init__(self, db: Session):
        self.db = db
        self.interview_service = InterviewService(db=db)

    def evaluate(self, user: User, session_id: int) -> dict[str, Any]:
        session = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.id == session_id, InterviewSession.user_id == user.id)
            .first()
        )
        if session is None:
            raise ValueError("Interview session not found")

        if session.status in ("active", "ready_to_finish"):
            result = self.interview_service.finish_session(user, session.preparation_id)
            feedback = result["feedback"]
        elif session.completed:
            feedback = (
                self.db.query(InterviewFeedback)
                .filter(InterviewFeedback.session_id == session.id, InterviewFeedback.user_id == user.id)
                .first()
            )
            if feedback is None:
                feedback = self._create_feedback_for_completed_session(user, session)
            else:
                feedback = self._refresh_feedback(user, feedback)
        else:
            raise ValueError("Session is not ready for evaluation")

        return self._serialize_detail(user, feedback)

    def get_history(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(InterviewFeedback).filter(InterviewFeedback.user_id == user.id)
        total = query.count()
        items = (
            query.order_by(InterviewFeedback.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return {
            "items": [self._serialize_history_item(item) for item in items],
            "total": total,
            "page": page,
            "size": size,
        }

    def get_by_id(self, user: User, feedback_id: int) -> dict[str, Any] | None:
        feedback = (
            self.db.query(InterviewFeedback)
            .filter(InterviewFeedback.id == feedback_id, InterviewFeedback.user_id == user.id)
            .first()
        )
        if feedback is None:
            return None
        return self._serialize_detail(user, feedback)

    def delete(self, user: User, feedback_id: int) -> None:
        feedback = (
            self.db.query(InterviewFeedback)
            .filter(InterviewFeedback.id == feedback_id, InterviewFeedback.user_id == user.id)
            .first()
        )
        if feedback is None:
            raise ValueError("Interview feedback not found")
        self.db.delete(feedback)
        self.db.commit()

    def get_progress(self, user: User) -> dict[str, Any]:
        stats = self.interview_service.get_statistics(user)
        feedback_items = (
            self.db.query(InterviewFeedback)
            .filter(InterviewFeedback.user_id == user.id)
            .order_by(InterviewFeedback.created_at.asc())
            .all()
        )

        overall_scores = [float(item.overall_score) for item in feedback_items if item.overall_score is not None]
        strongest_topics = stats.get("strongest_topics") or []
        weakest_topics = stats.get("weakest_topics") or []

        performance_breakdown: dict[str, float] = {}
        if feedback_items:
            latest = feedback_items[-1]
            breakdown_fields = {
                "technical": latest.technical_score,
                "communication": latest.communication_score,
                "confidence": latest.confidence_score,
                "grammar": latest.grammar_score,
                "clarity": latest.clarity_score,
                "problem_solving": latest.problem_solving_score,
            }
            performance_breakdown = {
                key: float(value) for key, value in breakdown_fields.items() if value is not None
            }

        return {
            "average_score": round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else None,
            "best_score": max(overall_scores) if overall_scores else None,
            "latest_score": overall_scores[-1] if overall_scores else None,
            "completed_interviews": len(feedback_items),
            "strongest_skill": strongest_topics[0]["topic"] if strongest_topics else None,
            "weakest_skill": weakest_topics[0]["topic"] if weakest_topics else None,
            "score_trend": [
                {
                    "feedback_id": item.id,
                    "date": item.created_at,
                    "overall_score": item.overall_score,
                }
                for item in feedback_items
            ],
            "skill_distribution": [
                {"skill": category, "score": score}
                for category, score in stats.get("category_breakdown", {}).items()
            ],
            "performance_breakdown": performance_breakdown,
        }

    def _create_feedback_for_completed_session(self, user: User, session: InterviewSession) -> InterviewFeedback:
        preparation = self.interview_service.get_preparation(user, session.preparation_id)
        if preparation is None:
            raise ValueError("Interview preparation not found")

        answers = self.db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).all()
        if not answers:
            raise ValueError("Cannot evaluate session without answers")

        feedback_payload = self.interview_service._build_session_feedback(preparation, answers)
        feedback = InterviewFeedback(
            session_id=session.id,
            preparation_id=session.preparation_id,
            user_id=user.id,
            **feedback_payload,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def _refresh_feedback(self, user: User, feedback: InterviewFeedback) -> InterviewFeedback:
        preparation = self.interview_service.get_preparation(user, feedback.preparation_id)
        if preparation is None:
            raise ValueError("Interview preparation not found")

        answers = self.db.query(InterviewAnswer).filter(InterviewAnswer.session_id == feedback.session_id).all()
        feedback_payload = self.interview_service._build_session_feedback(preparation, answers)
        for key, value in feedback_payload.items():
            setattr(feedback, key, value)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def _serialize_history_item(self, feedback: InterviewFeedback) -> dict[str, Any]:
        session = self.db.query(InterviewSession).filter(InterviewSession.id == feedback.session_id).first()
        job = self.db.query(Job).filter(Job.id == session.job_id).first() if session else None
        return {
            "id": feedback.id,
            "session_id": feedback.session_id,
            "preparation_id": feedback.preparation_id,
            "job_id": session.job_id if session else None,
            "company_name": job.company_name if job else None,
            "job_title": job.title if job else None,
            "overall_score": feedback.overall_score,
            "readiness_score": feedback.readiness_score,
            "confidence_score": feedback.confidence_score,
            "technical_score": feedback.technical_score,
            "communication_score": feedback.communication_score,
            "grammar_score": feedback.grammar_score,
            "clarity_score": feedback.clarity_score,
            "problem_solving_score": feedback.problem_solving_score,
            "created_at": feedback.created_at,
        }

    def _serialize_detail(self, user: User, feedback: InterviewFeedback) -> dict[str, Any]:
        session = self.db.query(InterviewSession).filter(InterviewSession.id == feedback.session_id).first()
        job = self.db.query(Job).filter(Job.id == session.job_id).first() if session else None
        answers = (
            self.db.query(InterviewAnswer)
            .filter(InterviewAnswer.session_id == feedback.session_id, InterviewAnswer.user_id == user.id)
            .order_by(InterviewAnswer.created_at.asc())
            .all()
        )

        question_reviews: list[dict[str, Any]] = []
        for answer in answers:
            question = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == answer.question_id).first()
            if question is None:
                continue
            question_reviews.append(
                {
                    "question_id": question.id,
                    "question_text": question.question_text,
                    "category": question.category,
                    "difficulty": question.difficulty,
                    "answer_text": answer.answer_text,
                    "ai_score": answer.ai_score,
                    "feedback": answer.feedback,
                    "strengths": answer.strengths or [],
                    "improvements": answer.improvements or [],
                    "time_spent_seconds": answer.time_spent_seconds,
                }
            )

        return {
            "id": feedback.id,
            "session_id": feedback.session_id,
            "preparation_id": feedback.preparation_id,
            "job_id": session.job_id if session else None,
            "company_name": job.company_name if job else None,
            "job_title": job.title if job else None,
            "overall_score": feedback.overall_score,
            "readiness_score": feedback.readiness_score,
            "confidence_score": feedback.confidence_score,
            "technical_score": feedback.technical_score,
            "communication_score": feedback.communication_score,
            "behavioral_score": feedback.behavioral_score,
            "grammar_score": feedback.grammar_score,
            "clarity_score": feedback.clarity_score,
            "problem_solving_score": feedback.problem_solving_score,
            "summary_feedback": feedback.summary_feedback,
            "strengths": feedback.strengths or [],
            "weaknesses": feedback.weaknesses or [],
            "improvement_suggestions": feedback.improvement_suggestions or [],
            "missing_skills": feedback.missing_skills or [],
            "important_topics": feedback.important_topics or [],
            "practice_recommendations": feedback.practice_recommendations or [],
            "recommended_resources": feedback.recommended_resources or [],
            "topics_to_improve": feedback.topics_to_improve or [],
            "score_breakdown": feedback.score_breakdown or {},
            "question_reviews": question_reviews,
            "created_at": feedback.created_at,
        }
