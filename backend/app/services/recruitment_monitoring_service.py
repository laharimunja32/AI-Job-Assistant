from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models.application import Application
from app.db.models.recruitment_monitoring import (
    Assessment,
    EmailEvent,
    Interview,
    NotificationHistory,
    Reminder,
    TimelineEvent,
)
from app.db.models.user import User
from app.schemas.recruitment_monitoring import (
    AssessmentCreate,
    AssessmentUpdate,
    EmailProcessRequest,
    InterviewCreate,
    InterviewUpdate,
    ReminderCreate,
    ReminderUpdate,
)


class RecruitmentMonitoringService:
    def __init__(self, db: Session):
        self.db = db

    def list_emails(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(EmailEvent).filter(EmailEvent.user_id == user.id).order_by(EmailEvent.received_time.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def get_email(self, user: User, email_id: int) -> EmailEvent | None:
        return self.db.query(EmailEvent).filter(EmailEvent.user_id == user.id, EmailEvent.id == email_id).first()

    def process_email(self, user: User, payload: EmailProcessRequest) -> EmailEvent:
        if not payload.authorization_confirmed:
            raise ValueError("Explicit user authorization is required before processing provider emails")

        extracted = self._extract_email_fields(payload.subject, payload.body)
        application_id = self._match_application(user.id, extracted["company_name"], extracted["job_title"], payload.subject)
        event_type = self._determine_event_type(extracted)
        body_preview = payload.body[:400] if payload.body else None

        email_event = EmailEvent(
            user_id=user.id,
            application_id=application_id,
            provider=payload.provider,
            company_name=extracted["company_name"],
            job_title=extracted["job_title"],
            sender=payload.sender,
            subject=payload.subject,
            body_preview=body_preview,
            received_time=payload.received_time,
            event_type=event_type,
            interview_invitation=extracted["interview_invitation"],
            online_assessment=extracted["online_assessment"],
            coding_test=extracted["coding_test"],
            hr_round=extracted["hr_round"],
            technical_round=extracted["technical_round"],
            offer=extracted["offer"],
            rejection=extracted["rejection"],
            deadline=extracted["deadline"],
            meeting_link=extracted["meeting_link"],
            metadata_json={"source": "official_provider_api"},
        )
        self.db.add(email_event)
        self.db.commit()
        self.db.refresh(email_event)

        if application_id is not None:
            self._create_timeline(
                user.id,
                application_id,
                self._timeline_type_from_email(event_type),
                title=payload.subject,
                description=f"Email from {payload.sender}",
                source_type="email",
                source_id=email_event.id,
                event_time=payload.received_time,
            )
        self._create_email_notifications(user.id, application_id, email_event)
        return email_event

    def list_assessments(self, user: User, page: int = 1, size: int = 20, status: str | None = None) -> dict[str, Any]:
        query = self.db.query(Assessment).filter(Assessment.user_id == user.id)
        if status:
            query = query.filter(Assessment.status == status.title())
        query = query.order_by(Assessment.deadline.asc().nullslast(), Assessment.created_at.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def create_assessment(self, user: User, payload: AssessmentCreate) -> Assessment:
        item = Assessment(user_id=user.id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        if item.application_id:
            self._create_timeline(
                user.id,
                item.application_id,
                "Assessment",
                title=item.assessment_type or "Assessment",
                description=f"Provider: {item.provider or 'Unknown'}",
                source_type="assessment",
                source_id=item.id,
                event_time=item.deadline or datetime.now(timezone.utc),
            )
        self._create_notification(
            user.id,
            item.application_id,
            "new_assessment",
            "New assessment",
            f"{item.assessment_type or 'Assessment'} is {item.status}",
        )
        return item

    def update_assessment(self, user: User, assessment_id: int, payload: AssessmentUpdate) -> Assessment:
        item = self.db.query(Assessment).filter(Assessment.user_id == user.id, Assessment.id == assessment_id).first()
        if item is None:
            raise ValueError("Assessment not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_interviews(self, user: User, page: int = 1, size: int = 20, status: str | None = None) -> dict[str, Any]:
        query = self.db.query(Interview).filter(Interview.user_id == user.id)
        if status:
            query = query.filter(Interview.status == status.title())
        query = query.order_by(Interview.interview_date.asc().nullslast(), Interview.created_at.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def create_interview(self, user: User, payload: InterviewCreate) -> Interview:
        item = Interview(user_id=user.id, **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        if item.application_id:
            self._create_timeline(
                user.id,
                item.application_id,
                "Interview",
                title=f"{item.interview_type} interview",
                description=f"Interviewer: {item.interviewer or 'TBD'}",
                source_type="interview",
                source_id=item.id,
                event_time=item.interview_date or datetime.now(timezone.utc),
            )
        self._create_notification(
            user.id,
            item.application_id,
            "interview_scheduled",
            "Interview scheduled",
            f"{item.interview_type} interview is {item.status}",
        )
        return item

    def update_interview(self, user: User, interview_id: int, payload: InterviewUpdate) -> Interview:
        item = self.db.query(Interview).filter(Interview.user_id == user.id, Interview.id == interview_id).first()
        if item is None:
            raise ValueError("Interview not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_timeline(self, user: User, application_id: int) -> dict[str, Any]:
        items = (
            self.db.query(TimelineEvent)
            .filter(TimelineEvent.user_id == user.id, TimelineEvent.application_id == application_id)
            .order_by(TimelineEvent.event_time.desc(), TimelineEvent.created_at.desc())
            .all()
        )
        return {"items": items, "total": len(items)}

    def list_reminders(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(Reminder).filter(Reminder.user_id == user.id).order_by(Reminder.due_at.asc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def create_reminder(self, user: User, payload: ReminderCreate) -> Reminder:
        item = Reminder(user_id=user.id, status="pending", **payload.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        if item.application_id:
            self._create_timeline(
                user.id,
                item.application_id,
                "Reminders",
                title=item.title,
                description=item.note,
                source_type="reminder",
                source_id=item.id,
                event_time=item.due_at,
            )
        self._create_notification(user.id, item.application_id, "reminder_due", "Reminder created", item.title)
        return item

    def update_reminder(self, user: User, reminder_id: int, payload: ReminderUpdate) -> Reminder:
        item = self.db.query(Reminder).filter(Reminder.user_id == user.id, Reminder.id == reminder_id).first()
        if item is None:
            raise ValueError("Reminder not found")
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(item, key, value)
        if payload.is_completed is not None:
            item.status = "completed" if payload.is_completed else "pending"
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_reminder(self, user: User, reminder_id: int) -> None:
        item = self.db.query(Reminder).filter(Reminder.user_id == user.id, Reminder.id == reminder_id).first()
        if item is None:
            raise ValueError("Reminder not found")
        self.db.delete(item)
        self.db.commit()

    def list_notifications(self, user: User, page: int = 1, size: int = 20) -> dict[str, Any]:
        query = self.db.query(NotificationHistory).filter(NotificationHistory.user_id == user.id).order_by(NotificationHistory.created_at.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": items, "total": total, "page": page, "size": size}

    def dashboard_summary(self, user: User) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        upcoming_cutoff = now + timedelta(days=7)
        assessments = (
            self.db.query(Assessment)
            .filter(
                Assessment.user_id == user.id,
                Assessment.deadline.isnot(None),
                Assessment.deadline >= now,
                Assessment.deadline <= upcoming_cutoff,
                Assessment.status.in_(["Pending", "Scheduled"]),
            )
            .count()
        )
        interviews = (
            self.db.query(Interview)
            .filter(
                Interview.user_id == user.id,
                Interview.interview_date.isnot(None),
                Interview.interview_date >= now,
                Interview.interview_date <= upcoming_cutoff,
                Interview.status == "Scheduled",
            )
            .count()
        )
        offers = self.db.query(EmailEvent).filter(EmailEvent.user_id == user.id, EmailEvent.offer.is_(True)).count()
        rejections = self.db.query(EmailEvent).filter(EmailEvent.user_id == user.id, EmailEvent.rejection.is_(True)).count()
        unread_emails = self.db.query(EmailEvent).filter(EmailEvent.user_id == user.id, EmailEvent.is_read.is_(False)).count()
        todays_deadlines = (
            self.db.query(Assessment)
            .filter(
                Assessment.user_id == user.id,
                Assessment.deadline.isnot(None),
                Assessment.deadline >= now.replace(hour=0, minute=0, second=0, microsecond=0),
                Assessment.deadline <= now.replace(hour=23, minute=59, second=59, microsecond=0),
            )
            .count()
        )
        recent_events = (
            self.db.query(TimelineEvent).filter(TimelineEvent.user_id == user.id).order_by(TimelineEvent.event_time.desc()).limit(8).all()
        )
        return {
            "upcoming_assessments": assessments,
            "upcoming_interviews": interviews,
            "offers": offers,
            "rejections": rejections,
            "unread_recruitment_emails": unread_emails,
            "todays_deadlines": todays_deadlines,
            "recent_timeline_events": [
                {
                    "id": event.id,
                    "application_id": event.application_id,
                    "event_type": event.event_type,
                    "title": event.title,
                    "event_time": event.event_time,
                }
                for event in recent_events
            ],
        }

    def _create_timeline(
        self,
        user_id: int,
        application_id: int,
        event_type: str,
        title: str,
        description: str | None,
        source_type: str,
        source_id: int,
        event_time: datetime,
    ) -> TimelineEvent:
        event = TimelineEvent(
            user_id=user_id,
            application_id=application_id,
            event_type=event_type,
            title=title[:255],
            description=description,
            source_type=source_type,
            source_id=source_id,
            event_time=event_time,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def _create_notification(self, user_id: int, application_id: int | None, notification_type: str, title: str, message: str) -> None:
        note = NotificationHistory(
            user_id=user_id,
            application_id=application_id,
            notification_type=notification_type,
            title=title,
            message=message,
        )
        self.db.add(note)
        self.db.commit()

    def _create_email_notifications(self, user_id: int, application_id: int | None, email_event: EmailEvent) -> None:
        if email_event.online_assessment:
            self._create_notification(user_id, application_id, "new_assessment", "New assessment", email_event.subject)
        if email_event.interview_invitation:
            self._create_notification(user_id, application_id, "interview_scheduled", "Interview invite", email_event.subject)
        if email_event.offer:
            self._create_notification(user_id, application_id, "offer_received", "Offer received", email_event.subject)
        if email_event.deadline:
            self._create_notification(user_id, application_id, "deadline_approaching", "Deadline detected", email_event.subject)

    def _timeline_type_from_email(self, event_type: str) -> str:
        mapping = {
            "assessment": "Assessment",
            "interview": "Interview",
            "offer": "Offer",
            "rejection": "Rejection",
        }
        return mapping.get(event_type, "Notes")

    def _extract_email_fields(self, subject: str, body: str) -> dict[str, Any]:
        combined = f"{subject}\n{body}"
        lower = combined.lower()
        company = self._extract_company(subject, body)
        job_title = self._extract_job_title(subject, body)
        deadline = self._extract_deadline(body)
        return {
            "company_name": company,
            "job_title": job_title,
            "interview_invitation": any(token in lower for token in ["interview", "meet with", "panel round"]),
            "online_assessment": any(token in lower for token in ["assessment", "hackerrank", "test link", "quiz"]),
            "coding_test": any(token in lower for token in ["coding test", "codility", "hackerank", "leetcode"]),
            "hr_round": "hr round" in lower or "human resources" in lower,
            "technical_round": "technical round" in lower or "tech interview" in lower,
            "offer": ("offer" in lower and "letter" in lower) or "congratulations" in lower,
            "rejection": "regret to inform" in lower or "not moving forward" in lower or "rejected" in lower,
            "deadline": deadline,
            "meeting_link": self._extract_meeting_link(body),
        }

    def _extract_company(self, subject: str, body: str) -> str | None:
        for text in (subject, body):
            match = re.search(r"(?:at|from)\s+([A-Z][A-Za-z0-9&.\- ]{2,60})", text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_job_title(self, subject: str, body: str) -> str | None:
        patterns = [
            r"for\s+the\s+role\s+of\s+([A-Za-z0-9 /&\-]{3,80})",
            r"position:\s*([A-Za-z0-9 /&\-]{3,80})",
            r"role:\s*([A-Za-z0-9 /&\-]{3,80})",
        ]
        for text in (subject, body):
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return None

    def _extract_deadline(self, text: str) -> datetime | None:
        match = re.search(r"deadline[:\s]+(\d{4}-\d{2}-\d{2})", text, flags=re.IGNORECASE)
        if not match:
            return None
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _extract_meeting_link(self, text: str) -> str | None:
        match = re.search(r"https?://[^\s]+", text)
        return match.group(0) if match else None

    def _determine_event_type(self, fields: dict[str, Any]) -> str:
        if fields["offer"]:
            return "offer"
        if fields["rejection"]:
            return "rejection"
        if fields["interview_invitation"]:
            return "interview"
        if fields["online_assessment"] or fields["coding_test"]:
            return "assessment"
        return "general"

    def _match_application(self, user_id: int, company_name: str | None, job_title: str | None, subject: str) -> int | None:
        query = self.db.query(Application).filter(Application.user_id == user_id, Application.is_deleted.is_(False))
        conditions = []
        if company_name:
            conditions.append(Application.company_name.ilike(f"%{company_name}%"))
        if job_title:
            conditions.append(Application.job_title.ilike(f"%{job_title}%"))
        if conditions:
            app = query.filter(or_(*conditions)).order_by(Application.updated_at.desc()).first()
            if app:
                return app.id
        fallback = query.filter(
            or_(
                Application.company_name.ilike(f"%{subject[:40]}%"),
                Application.job_title.ilike(f"%{subject[:40]}%"),
            )
        ).first()
        return fallback.id if fallback else None
