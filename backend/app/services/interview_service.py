from __future__ import annotations

import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.application import Application
from app.db.models.cover_letter import GeneratedCoverLetter
from app.db.models.interview import (
    InterviewAnswer,
    InterviewFeedback,
    InterviewPreparation,
    InterviewQuestion,
    InterviewSession,
)
from app.db.models.job import Job
from app.db.models.profile import Profile
from app.db.models.resume import Resume
from app.db.models.resume_tailoring import TailoredResume
from app.db.models.user import User
from app.db.session import SessionLocal
from app.services.jobs.match_service import JobMatch

_GENERATION_EXECUTOR = ThreadPoolExecutor(max_workers=2)

QUESTION_CATEGORIES = [
    "company_specific",
    "hr",
    "behavioral",
    "technical",
    "project",
    "resume_based",
]


class InterviewService:
    def __init__(self, db: Session):
        self.db = db

    def generate_for_job(self, user: User, job_id: int, application_id: int | None = None) -> dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job is None:
            raise ValueError("Job not found")

        resume = (
            self.db.query(Resume)
            .filter(Resume.user_id == user.id, Resume.is_active.is_(True))
            .order_by(Resume.version.desc())
            .first()
        )
        if resume is None:
            raise ValueError("Active resume not found")

        profile = self.db.query(Profile).filter(Profile.user_id == user.id).first()
        tailored_resume = (
            self.db.query(TailoredResume)
            .filter(TailoredResume.user_id == user.id, TailoredResume.job_id == job.id, TailoredResume.status == "completed")
            .order_by(TailoredResume.resume_version.desc())
            .first()
        )
        cover_letter = (
            self.db.query(GeneratedCoverLetter)
            .filter(GeneratedCoverLetter.user_id == user.id, GeneratedCoverLetter.job_id == job.id, GeneratedCoverLetter.status == "completed")
            .order_by(GeneratedCoverLetter.cover_letter_version.desc())
            .first()
        )
        application = None
        if application_id is not None:
            application = (
                self.db.query(Application)
                .filter(Application.id == application_id, Application.user_id == user.id, Application.is_deleted.is_(False))
                .first()
            )
            if application is None:
                raise ValueError("Application not found")

        signature = self._build_generation_signature(user.id, job, resume, profile, tailored_resume, cover_letter)
        cached = (
            self.db.query(InterviewPreparation)
            .filter(
                InterviewPreparation.user_id == user.id,
                InterviewPreparation.job_id == job.id,
                InterviewPreparation.generation_signature == signature,
                InterviewPreparation.status == "completed",
            )
            .order_by(InterviewPreparation.preparation_version.desc())
            .first()
        )
        if cached:
            return {
                "preparation_id": cached.id,
                "status": cached.status,
                "cached": True,
                "message": "A matching interview preparation already exists and was reused.",
            }

        version = self._next_version(user.id, job.id)
        preparation = InterviewPreparation(
            user_id=user.id,
            job_id=job.id,
            application_id=application.id if application else None,
            tailored_resume_id=tailored_resume.id if tailored_resume else None,
            cover_letter_id=cover_letter.id if cover_letter else None,
            preparation_version=version,
            status="queued",
            generation_signature=signature,
        )
        self.db.add(preparation)
        self.db.commit()
        self.db.refresh(preparation)

        _GENERATION_EXECUTOR.submit(self._run_generation_task, preparation.id)
        return {
            "preparation_id": preparation.id,
            "status": "queued",
            "cached": False,
            "message": "Interview preparation generation started.",
        }

    def get_preparation(self, user: User, preparation_id: int) -> InterviewPreparation | None:
        return (
            self.db.query(InterviewPreparation)
            .filter(InterviewPreparation.id == preparation_id, InterviewPreparation.user_id == user.id)
            .first()
        )

    def get_questions(self, user: User, preparation_id: int) -> list[InterviewQuestion]:
        preparation = self.get_preparation(user, preparation_id)
        if preparation is None:
            return []
        return (
            self.db.query(InterviewQuestion)
            .filter(InterviewQuestion.preparation_id == preparation.id, InterviewQuestion.user_id == user.id)
            .order_by(InterviewQuestion.sort_order.asc())
            .all()
        )

    def get_history(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(InterviewSession).filter(InterviewSession.user_id == user.id, InterviewSession.completed.is_(True))
        total = query.count()
        items = query.order_by(InterviewSession.completed_at.desc()).offset((page - 1) * size).limit(size).all()
        serialized = [self._serialize_history_item(item) for item in items]
        return {"items": serialized, "total": total, "page": page, "size": size}

    def delete_preparation(self, user: User, preparation_id: int) -> None:
        preparation = self.get_preparation(user, preparation_id)
        if preparation is None:
            raise ValueError("Interview preparation not found")

        session_ids = [
            row.id
            for row in self.db.query(InterviewSession).filter(InterviewSession.preparation_id == preparation.id).all()
        ]
        if session_ids:
            self.db.query(InterviewAnswer).filter(InterviewAnswer.session_id.in_(session_ids)).delete(synchronize_session=False)
            self.db.query(InterviewFeedback).filter(InterviewFeedback.session_id.in_(session_ids)).delete(synchronize_session=False)
            self.db.query(InterviewSession).filter(InterviewSession.id.in_(session_ids)).delete(synchronize_session=False)

        self.db.query(InterviewQuestion).filter(InterviewQuestion.preparation_id == preparation.id).delete()
        self.db.delete(preparation)
        self.db.commit()

    def start_session(self, user: User, preparation_id: int) -> dict[str, Any]:
        preparation = self.get_preparation(user, preparation_id)
        if preparation is None:
            raise ValueError("Interview preparation not found")
        if preparation.status != "completed":
            raise ValueError("Interview preparation is not ready yet")

        questions = self.get_questions(user, preparation_id)
        if not questions:
            raise ValueError("No interview questions available")

        session = InterviewSession(
            preparation_id=preparation.id,
            user_id=user.id,
            job_id=preparation.job_id,
            status="active",
            current_question_index=0,
            total_questions=len(questions),
            started_at=datetime.utcnow(),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        first_question = questions[0]
        return {
            "session": session,
            "current_question": first_question,
            "progress": self._session_progress(session),
        }

    def submit_answer(
        self,
        user: User,
        preparation_id: int,
        *,
        answer_text: str,
        time_spent_seconds: int | None = None,
    ) -> dict[str, Any]:
        session = self._get_active_session(user, preparation_id)
        questions = self.get_questions(user, preparation_id)
        if session.current_question_index >= len(questions):
            raise ValueError("All questions have been answered")

        question = questions[session.current_question_index]
        score_result = self._score_answer(question, answer_text)

        answer = InterviewAnswer(
            session_id=session.id,
            question_id=question.id,
            user_id=user.id,
            answer_text=answer_text,
            ai_score=score_result["ai_score"],
            feedback=score_result["feedback"],
            strengths=score_result["strengths"],
            improvements=score_result["improvements"],
            time_spent_seconds=time_spent_seconds,
        )
        self.db.add(answer)

        session.questions_answered += 1
        session.current_question_index += 1
        if session.current_question_index >= len(questions):
            session.status = "ready_to_finish"
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        self.db.refresh(answer)

        next_question = questions[session.current_question_index] if session.current_question_index < len(questions) else None
        return {
            "answer": answer,
            "session": session,
            "next_question": next_question,
            "progress": self._session_progress(session),
        }

    def finish_session(self, user: User, preparation_id: int) -> dict[str, Any]:
        session = self._get_active_session(user, preparation_id, allow_ready=True)
        preparation = self.get_preparation(user, preparation_id)
        if preparation is None:
            raise ValueError("Interview preparation not found")

        answers = self.db.query(InterviewAnswer).filter(InterviewAnswer.session_id == session.id).all()
        feedback_payload = self._build_session_feedback(preparation, answers)

        feedback = InterviewFeedback(
            session_id=session.id,
            preparation_id=preparation.id,
            user_id=user.id,
            **feedback_payload,
        )
        self.db.add(feedback)

        session.status = "completed"
        session.completed = True
        session.completed_at = datetime.utcnow()
        if session.started_at:
            session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())
        self.db.add(session)

        preparation.completed = True
        preparation.readiness_score = feedback.readiness_score
        preparation.confidence_score = feedback.confidence_score
        preparation.technical_score = feedback.technical_score
        preparation.communication_score = feedback.communication_score
        preparation.behavioral_score = feedback.behavioral_score
        self.db.add(preparation)
        self.db.commit()
        self.db.refresh(feedback)
        self.db.refresh(session)

        return {"session": session, "feedback": feedback}

    def get_feedback(self, user: User, preparation_id: int) -> InterviewFeedback | None:
        session = (
            self.db.query(InterviewSession)
            .filter(
                InterviewSession.preparation_id == preparation_id,
                InterviewSession.user_id == user.id,
                InterviewSession.completed.is_(True),
            )
            .order_by(InterviewSession.completed_at.desc())
            .first()
        )
        if session is None:
            return None
        return (
            self.db.query(InterviewFeedback)
            .filter(InterviewFeedback.session_id == session.id, InterviewFeedback.user_id == user.id)
            .first()
        )

    def get_statistics(self, user: User) -> dict[str, Any]:
        preparations = self.db.query(InterviewPreparation).filter(InterviewPreparation.user_id == user.id).all()
        sessions = self.db.query(InterviewSession).filter(InterviewSession.user_id == user.id, InterviewSession.completed.is_(True)).all()
        feedback_items = self.db.query(InterviewFeedback).filter(InterviewFeedback.user_id == user.id).all()

        readiness_scores = [float(item.readiness_score) for item in feedback_items if item.readiness_score is not None]
        confidence_scores = [float(item.confidence_score) for item in feedback_items if item.confidence_score is not None]
        questions_answered = sum(session.questions_answered for session in sessions)

        category_scores: dict[str, list[float]] = {}
        for answer in self.db.query(InterviewAnswer).filter(InterviewAnswer.user_id == user.id).all():
            question = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == answer.question_id).first()
            if question and answer.ai_score is not None:
                category_scores.setdefault(question.category, []).append(float(answer.ai_score))

        strongest_topics = sorted(
            [(cat, round(sum(scores) / len(scores), 1)) for cat, scores in category_scores.items()],
            key=lambda pair: pair[1],
            reverse=True,
        )[:5]
        weakest_topics = sorted(
            [(cat, round(sum(scores) / len(scores), 1)) for cat, scores in category_scores.items()],
            key=lambda pair: pair[1],
        )[:5]

        return {
            "total_preparations": len(preparations),
            "completed_preparations": sum(1 for item in preparations if item.status == "completed"),
            "practice_sessions": len(sessions),
            "questions_answered": questions_answered,
            "average_readiness": round(sum(readiness_scores) / len(readiness_scores), 1) if readiness_scores else None,
            "average_confidence": round(sum(confidence_scores) / len(confidence_scores), 1) if confidence_scores else None,
            "strongest_topics": [{"topic": cat, "score": score} for cat, score in strongest_topics],
            "weakest_topics": [{"topic": cat, "score": score} for cat, score in weakest_topics],
            "category_breakdown": {
                cat: round(sum(scores) / len(scores), 1) for cat, scores in category_scores.items()
            },
        }

    def recent_for_dashboard(self, user: User, limit: int = 5) -> list[dict[str, Any]]:
        sessions = (
            self.db.query(InterviewSession)
            .filter(InterviewSession.user_id == user.id, InterviewSession.completed.is_(True))
            .order_by(InterviewSession.completed_at.desc())
            .limit(limit)
            .all()
        )
        result: list[dict[str, Any]] = []
        for session in sessions:
            job = self.db.query(Job).filter(Job.id == session.job_id).first()
            feedback = (
                self.db.query(InterviewFeedback)
                .filter(InterviewFeedback.session_id == session.id)
                .first()
            )
            result.append(
                {
                    "id": session.id,
                    "preparation_id": session.preparation_id,
                    "job_id": session.job_id,
                    "company_name": job.company_name if job else None,
                    "job_title": job.title if job else None,
                    "overall_score": feedback.overall_score if feedback else None,
                    "readiness_score": feedback.readiness_score if feedback else None,
                    "questions_answered": session.questions_answered,
                    "duration_seconds": session.duration_seconds,
                    "completed_at": session.completed_at,
                }
            )
        return result

    def stats_for_dashboard(self, user: User) -> dict[str, Any]:
        stats = self.get_statistics(user)
        return {
            "total_preparations": stats["total_preparations"],
            "practice_sessions": stats["practice_sessions"],
            "questions_answered": stats["questions_answered"],
            "average_readiness": stats["average_readiness"],
            "average_confidence": stats["average_confidence"],
            "strongest_topics": stats["strongest_topics"],
            "weakest_topics": stats["weakest_topics"],
        }

    def summaries_for_jobs(self, user: User, job_ids: list[int]) -> dict[int, dict[str, Any]]:
        if not job_ids:
            return {}

        preparations = (
            self.db.query(InterviewPreparation)
            .filter(
                InterviewPreparation.user_id == user.id,
                InterviewPreparation.job_id.in_(job_ids),
                InterviewPreparation.status == "completed",
            )
            .order_by(InterviewPreparation.job_id.asc(), InterviewPreparation.created_at.desc())
            .all()
        )
        prep_by_job: dict[int, InterviewPreparation] = {}
        for preparation in preparations:
            if preparation.job_id not in prep_by_job:
                prep_by_job[preparation.job_id] = preparation

        sessions = (
            self.db.query(InterviewSession)
            .filter(
                InterviewSession.user_id == user.id,
                InterviewSession.job_id.in_(job_ids),
                InterviewSession.completed.is_(True),
            )
            .all()
        )
        session_counts: dict[int, int] = {}
        completed_jobs: set[int] = set()
        for session in sessions:
            session_counts[session.job_id] = session_counts.get(session.job_id, 0) + 1
            completed_jobs.add(session.job_id)

        summaries: dict[int, dict[str, Any]] = {}
        for job_id in job_ids:
            preparation = prep_by_job.get(job_id)
            summaries[job_id] = {
                "interview_prepared": preparation is not None,
                "interview_completed": job_id in completed_jobs,
                "interview_readiness_score": preparation.readiness_score if preparation else None,
                "interview_practice_sessions": session_counts.get(job_id, 0),
                "interview_preparation_id": preparation.id if preparation else None,
            }
        return summaries

    def _run_generation_task(self, preparation_id: int) -> None:
        db = SessionLocal()
        try:
            self._execute_generation(db, preparation_id)
        finally:
            db.close()

    def _execute_generation(self, db: Session, preparation_id: int) -> None:
        try:
            preparation = db.query(InterviewPreparation).filter(InterviewPreparation.id == preparation_id).first()
            if preparation is None:
                return

            preparation.status = "processing"
            db.add(preparation)
            db.commit()

            job = db.query(Job).filter(Job.id == preparation.job_id).first()
            profile = db.query(Profile).filter(Profile.user_id == preparation.user_id).first()
            resume = (
                db.query(Resume)
                .filter(Resume.user_id == preparation.user_id, Resume.is_active.is_(True))
                .order_by(Resume.version.desc())
                .first()
            )
            tailored_resume = (
                db.query(TailoredResume).filter(TailoredResume.id == preparation.tailored_resume_id).first()
                if preparation.tailored_resume_id
                else None
            )
            cover_letter = (
                db.query(GeneratedCoverLetter).filter(GeneratedCoverLetter.id == preparation.cover_letter_id).first()
                if preparation.cover_letter_id
                else None
            )
            match = db.query(JobMatch).filter(JobMatch.user_id == preparation.user_id, JobMatch.job_id == preparation.job_id).first()

            if job is None or resume is None:
                preparation.status = "failed"
                db.add(preparation)
                db.commit()
                return

            context = self._build_context(job, resume, profile, tailored_resume, cover_letter, match)
            questions = self._generate_questions(context)
            analysis = self._generate_analysis(context)
            scores = self._compute_preparation_scores(context, analysis)

            for index, question_data in enumerate(questions):
                question = InterviewQuestion(
                    preparation_id=preparation.id,
                    user_id=preparation.user_id,
                    category=question_data["category"],
                    question_text=question_data["question_text"],
                    difficulty=question_data["difficulty"],
                    follow_up_questions=question_data.get("follow_up_questions", []),
                    hints=question_data.get("hints", []),
                    sort_order=index,
                )
                db.add(question)

            preparation.analysis = analysis
            preparation.strengths = analysis.get("strengths", [])
            preparation.weaknesses = analysis.get("weaknesses", [])
            preparation.recommendations = analysis.get("recommendations", [])
            preparation.star_examples = analysis.get("star_examples", [])
            preparation.recommended_topics = analysis.get("recommended_topics", [])
            preparation.important_topics = analysis.get("important_topics", [])
            preparation.missing_skills = analysis.get("missing_skills", [])
            preparation.practice_recommendations = analysis.get("practice_recommendations", [])
            preparation.estimated_duration_minutes = max(15, len(questions) * 4)
            preparation.readiness_score = scores["readiness_score"]
            preparation.confidence_score = scores["confidence_score"]
            preparation.technical_score = scores["technical_score"]
            preparation.communication_score = scores["communication_score"]
            preparation.behavioral_score = scores["behavioral_score"]
            preparation.status = "completed"
            preparation.generated_at = datetime.utcnow()
            db.add(preparation)
            db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
            failed = db.query(InterviewPreparation).filter(InterviewPreparation.id == preparation_id).first()
            if failed:
                failed.status = "failed"
                db.add(failed)
                db.commit()

    def _build_generation_signature(
        self,
        user_id: int,
        job: Job,
        resume: Resume,
        profile: Profile | None,
        tailored_resume: TailoredResume | None,
        cover_letter: GeneratedCoverLetter | None,
    ) -> str:
        payload = "|".join(
            [
                str(user_id),
                str(job.id),
                str(job.updated_at or ""),
                str(resume.id),
                str(resume.updated_at or ""),
                str(profile.updated_at if profile else ""),
                str(tailored_resume.updated_at if tailored_resume else ""),
                str(cover_letter.updated_at if cover_letter else ""),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _next_version(self, user_id: int, job_id: int) -> int:
        latest = (
            self.db.query(InterviewPreparation)
            .filter(InterviewPreparation.user_id == user_id, InterviewPreparation.job_id == job_id)
            .order_by(InterviewPreparation.preparation_version.desc())
            .first()
        )
        return (latest.preparation_version if latest else 0) + 1

    def _build_context(
        self,
        job: Job,
        resume: Resume,
        profile: Profile | None,
        tailored_resume: TailoredResume | None,
        cover_letter: GeneratedCoverLetter | None,
        match: JobMatch | None,
    ) -> dict[str, Any]:
        resume_text = self._extract_resume_text(resume)
        if tailored_resume and tailored_resume.markdown_content:
            resume_text = tailored_resume.markdown_content
        cover_letter_text = cover_letter.markdown_content if cover_letter and cover_letter.markdown_content else ""
        skills = list(dict.fromkeys((profile.skills if profile else []) + (job.skills or []) + (job.tags or [])))
        ats_keywords: list[str] = []
        if tailored_resume and isinstance(tailored_resume.analysis, dict):
            ats_keywords = tailored_resume.analysis.get("keywords", [])[:15]
        elif job.description:
            ats_keywords = self._extract_keywords(job.description)[:15]

        return {
            "job": job,
            "resume_text": resume_text,
            "cover_letter_text": cover_letter_text,
            "profile": profile,
            "skills": skills,
            "ats_keywords": ats_keywords,
            "match_score": match.score if match else None,
            "projects": profile.projects if profile else [],
        }

    def _generate_questions(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        job: Job = context["job"]
        skills = context["skills"][:6]
        projects = context["projects"][:3]
        company = job.company_name or "the company"
        title = job.title or "this role"

        questions: list[dict[str, Any]] = [
            {
                "category": "company_specific",
                "question_text": f"Why do you want to work at {company} as a {title}?",
                "difficulty": "medium",
                "follow_up_questions": [f"What do you know about {company}'s products or services?"],
                "hints": ["Connect company mission to your career goals."],
            },
            {
                "category": "hr",
                "question_text": "Tell me about yourself and your career journey so far.",
                "difficulty": "easy",
                "follow_up_questions": ["What motivates you in your next role?"],
                "hints": ["Keep it concise and role-focused."],
            },
            {
                "category": "behavioral",
                "question_text": "Describe a time you handled a challenging situation under pressure.",
                "difficulty": "medium",
                "follow_up_questions": ["What would you do differently next time?"],
                "hints": ["Use the STAR method."],
            },
        ]

        for skill in skills[:3]:
            questions.append(
                {
                    "category": "technical",
                    "question_text": f"Explain your experience with {skill} and how you have applied it in production.",
                    "difficulty": "hard",
                    "follow_up_questions": [f"What trade-offs have you managed while using {skill}?"],
                    "hints": [f"Mention concrete outcomes using {skill}."],
                }
            )

        for project in projects:
            if isinstance(project, dict) and project.get("name"):
                questions.append(
                    {
                        "category": "project",
                        "question_text": f"Walk me through your role in the {project['name']} project.",
                        "difficulty": "medium",
                        "follow_up_questions": ["What was the biggest technical challenge?"],
                        "hints": ["Highlight ownership, impact, and metrics."],
                    }
                )

        questions.append(
            {
                "category": "resume_based",
                "question_text": "Which accomplishment on your resume best demonstrates your fit for this role?",
                "difficulty": "medium",
                "follow_up_questions": ["How did you measure success?"],
                "hints": ["Pick an achievement aligned with the job description."],
            }
        )

        return questions[:12]

    def _generate_analysis(self, context: dict[str, Any]) -> dict[str, Any]:
        job: Job = context["job"]
        skills = context["skills"]
        job_skills = job.skills or []
        missing_skills = [skill for skill in job_skills if skill not in skills][:6]
        important_topics = list(dict.fromkeys((job_skills or []) + (context["ats_keywords"] or [])))[:8]

        return {
            "strengths": [
                f"Strong alignment with {job.title} requirements.",
                "Relevant project and resume evidence available for behavioral answers.",
                "Profile skills map well to role-critical technologies.",
            ],
            "weaknesses": [
                f"Practice articulating experience with {skill}." for skill in missing_skills[:3]
            ] or ["Prepare more company-specific talking points."],
            "recommendations": [
                "Practice 2-3 STAR stories tied to the job description.",
                "Review your tailored resume bullets before the interview.",
                "Prepare thoughtful questions for the interviewer.",
            ],
            "star_examples": [
                {
                    "situation": "A production issue affected service reliability.",
                    "task": "Lead diagnosis and restore stable operations.",
                    "action": "Coordinated debugging, implemented fix, and added monitoring.",
                    "result": "Reduced incident recurrence and improved response time.",
                }
            ],
            "recommended_topics": important_topics[:6],
            "important_topics": important_topics,
            "missing_skills": missing_skills,
            "practice_recommendations": [
                "Run one timed mock interview session.",
                "Record answers for communication review.",
                "Review HR and behavioral questions daily until the interview.",
            ],
        }

    def _compute_preparation_scores(self, context: dict[str, Any], analysis: dict[str, Any]) -> dict[str, float]:
        job_skills = context["job"].skills or []
        user_skills = context["skills"]
        overlap = len([skill for skill in job_skills if skill in user_skills])
        skill_ratio = overlap / max(1, len(job_skills))
        match_bonus = (context["match_score"] or 70) / 100

        readiness = round(min(95.0, 55.0 + skill_ratio * 25.0 + match_bonus * 15.0), 1)
        confidence = round(min(92.0, 50.0 + skill_ratio * 20.0 + (10 if context["cover_letter_text"] else 0)), 1)
        technical = round(min(94.0, 52.0 + skill_ratio * 30.0), 1)
        communication = round(min(90.0, 58.0 + (8 if context["cover_letter_text"] else 0) + skill_ratio * 10.0), 1)
        behavioral = round(min(91.0, 56.0 + (6 if context["projects"] else 0) + skill_ratio * 12.0), 1)

        return {
            "readiness_score": readiness,
            "confidence_score": confidence,
            "technical_score": technical,
            "communication_score": communication,
            "behavioral_score": behavioral,
        }

    def _score_answer(self, question: InterviewQuestion, answer_text: str) -> dict[str, Any]:
        text = (answer_text or "").strip()
        word_count = len(text.split())
        base = 45.0
        if word_count >= 40:
            base += 20.0
        elif word_count >= 20:
            base += 12.0
        elif word_count >= 8:
            base += 6.0

        category_bonus = {
            "technical": 8.0,
            "behavioral": 6.0,
            "project": 7.0,
            "company_specific": 5.0,
            "hr": 4.0,
            "resume_based": 5.0,
        }.get(question.category, 4.0)

        if "because" in text.lower() or "result" in text.lower():
            base += 5.0

        ai_score = round(min(98.0, base + category_bonus), 1)
        return {
            "ai_score": ai_score,
            "feedback": "Good structure. Add measurable outcomes to strengthen this answer." if ai_score >= 70 else "Expand with a concrete example and outcome.",
            "strengths": ["Clear response"] if word_count >= 15 else [],
            "improvements": ["Add metrics or STAR structure."] if ai_score < 80 else [],
        }

    def _build_session_feedback(self, preparation: InterviewPreparation, answers: list[InterviewAnswer]) -> dict[str, Any]:
        scores = [float(answer.ai_score) for answer in answers if answer.ai_score is not None]
        overall = round(sum(scores) / len(scores), 1) if scores else preparation.readiness_score or 70.0

        category_scores: dict[str, list[float]] = {}
        for answer in answers:
            question = self.db.query(InterviewQuestion).filter(InterviewQuestion.id == answer.question_id).first()
            if question and answer.ai_score is not None:
                category_scores.setdefault(question.category, []).append(float(answer.ai_score))

        technical_scores = category_scores.get("technical", []) + category_scores.get("project", [])
        behavioral_scores = category_scores.get("behavioral", []) + category_scores.get("hr", [])
        communication_scores = scores

        def avg(values: list[float], fallback: float | None) -> float | None:
            if not values:
                return fallback
            return round(sum(values) / len(values), 1)

        readiness = avg(scores, preparation.readiness_score)
        confidence = round(min(95.0, (readiness or overall) * 0.95), 1) if readiness else preparation.confidence_score
        technical = avg(technical_scores, preparation.technical_score)
        communication = avg(communication_scores, preparation.communication_score)
        behavioral = avg(behavioral_scores, preparation.behavioral_score)

        weakest = sorted(
            [(cat, round(sum(vals) / len(vals), 1)) for cat, vals in category_scores.items()],
            key=lambda pair: pair[1],
        )[:4]

        return {
            "overall_score": overall,
            "readiness_score": readiness,
            "confidence_score": confidence,
            "technical_score": technical,
            "communication_score": communication,
            "behavioral_score": behavioral,
            "strengths": preparation.strengths or [],
            "weaknesses": preparation.weaknesses or [],
            "improvement_suggestions": (preparation.recommendations or []) + ["Review answers with lower AI scores."],
            "missing_skills": preparation.missing_skills or [],
            "important_topics": preparation.important_topics or [],
            "practice_recommendations": preparation.practice_recommendations or [],
            "recommended_resources": [
                "Company careers page and recent news",
                "Role-specific technical documentation",
                "STAR method interview worksheet",
            ],
            "topics_to_improve": [topic for topic, _ in weakest],
            "score_breakdown": {cat: round(sum(vals) / len(vals), 1) for cat, vals in category_scores.items()},
        }

    def _get_active_session(self, user: User, preparation_id: int, allow_ready: bool = False) -> InterviewSession:
        statuses = ["active", "ready_to_finish"] if allow_ready else ["active"]
        session = (
            self.db.query(InterviewSession)
            .filter(
                InterviewSession.preparation_id == preparation_id,
                InterviewSession.user_id == user.id,
                InterviewSession.status.in_(statuses),
            )
            .order_by(InterviewSession.created_at.desc())
            .first()
        )
        if session is None:
            raise ValueError("No active interview session found")
        return session

    def _session_progress(self, session: InterviewSession) -> dict[str, Any]:
        total = max(session.total_questions, 1)
        return {
            "current_index": session.current_question_index,
            "total_questions": session.total_questions,
            "questions_answered": session.questions_answered,
            "percent_complete": round((session.questions_answered / total) * 100, 1),
        }

    def _serialize_history_item(self, session: InterviewSession) -> dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == session.job_id).first()
        feedback = self.db.query(InterviewFeedback).filter(InterviewFeedback.session_id == session.id).first()
        return {
            "id": session.id,
            "preparation_id": session.preparation_id,
            "job_id": session.job_id,
            "company_name": job.company_name if job else None,
            "job_title": job.title if job else None,
            "overall_score": feedback.overall_score if feedback else None,
            "readiness_score": feedback.readiness_score if feedback else None,
            "confidence_score": feedback.confidence_score if feedback else None,
            "questions_answered": session.questions_answered,
            "duration_seconds": session.duration_seconds,
            "completed_at": session.completed_at,
        }

    def _extract_resume_text(self, resume: Resume) -> str:
        metadata = resume.file_metadata or {}
        content = metadata.get("content")
        if isinstance(content, str) and content.strip():
            return content
        return ""

    def _extract_keywords(self, text: str) -> list[str]:
        words = [w.strip() for w in re.split(r"[^A-Za-z0-9+#.]+", text) if w.strip()]
        noise = {"and", "the", "for", "with", "role", "work", "will", "your", "you", "our", "are"}
        result: list[str] = []
        for word in words:
            if len(word) < 3 or word.lower() in noise:
                continue
            if word not in result:
                result.append(word)
        return result
