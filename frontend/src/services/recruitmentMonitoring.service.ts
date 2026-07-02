import api from './api';
import type { Assessment, EmailEvent, Interview, NotificationHistory, PaginatedResponse, Reminder, TimelineEvent } from '@/types';

export interface EmailProcessPayload {
  provider: string;
  authorization_confirmed: boolean;
  sender: string;
  subject: string;
  body: string;
  received_time: string;
}

export interface AssessmentPayload {
  application_id?: number | null;
  email_event_id?: number | null;
  provider?: string | null;
  assessment_url?: string | null;
  assessment_type?: string | null;
  duration_minutes?: number | null;
  deadline?: string | null;
  status?: string;
  notes?: string | null;
}

export interface InterviewPayload {
  application_id?: number | null;
  email_event_id?: number | null;
  interview_type: string;
  interview_date?: string | null;
  interview_time?: string | null;
  time_zone?: string | null;
  meeting_link?: string | null;
  interviewer?: string | null;
  notes?: string | null;
  status?: string;
}

export type InterviewUpdatePayload = Partial<InterviewPayload>;

export interface ReminderPayload {
  application_id?: number | null;
  timeline_event_id?: number | null;
  title: string;
  note?: string | null;
  due_at: string;
}

export const recruitmentMonitoringService = {
  listEmails: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<EmailEvent>>('/emails', { params }),
  getEmailById: (id: number) => api.get<EmailEvent>(`/emails/${id}`),
  processEmail: (payload: EmailProcessPayload) => api.post<EmailEvent>('/emails/process', payload),

  listAssessments: (params?: { page?: number; size?: number; status?: string }) =>
    api.get<PaginatedResponse<Assessment>>('/assessments', { params }),
  createAssessment: (payload: AssessmentPayload) => api.post<Assessment>('/assessments', payload),
  updateAssessment: (id: number, payload: AssessmentPayload) => api.put<Assessment>(`/assessments/${id}`, payload),

  listInterviews: (params?: { page?: number; size?: number; status?: string }) =>
    api.get<PaginatedResponse<Interview>>('/interviews', { params }),
  createInterview: (payload: InterviewPayload) => api.post<Interview>('/interviews', payload),
  updateInterview: (id: number, payload: InterviewUpdatePayload) => api.put<Interview>(`/interviews/${id}`, payload),

  getTimeline: (application_id: number) =>
    api.get<{ items: TimelineEvent[]; total: number }>(`/timeline/${application_id}`),

  listReminders: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<Reminder>>('/reminders', { params }),
  createReminder: (payload: ReminderPayload) => api.post<Reminder>('/reminders', payload),
  updateReminder: (id: number, payload: Partial<ReminderPayload> & { is_completed?: boolean; status?: string }) =>
    api.put<Reminder>(`/reminders/${id}`, payload),
  deleteReminder: (id: number) => api.delete(`/reminders/${id}`),

  listNotificationHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<NotificationHistory>>('/notifications/history', { params }),
};
