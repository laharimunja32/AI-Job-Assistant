import api from './api';
import type {
  BrowserSession,
  BrowserSessionListResponse,
  BrowserStatusSummary,
  BrowserType,
  BrowserReviewConfirmResponse,
  BrowserReviewReport,
  FormDetectionResponse,
  FormFillResponse,
  SubmissionAuditHistoryResponse,
  SubmissionValidationReport,
  UploadDetectionResponse,
  UploadStatusResponse,
} from '@/types';

export const browserService = {
  createSession: (payload?: { browser_type?: BrowserType; application_id?: number }) =>
    api.post<BrowserSession>('/browser/session', payload ?? {}),

  openApplication: (applicationId: number, payload?: { session_id?: string; browser_type?: BrowserType }) =>
    api.post<BrowserSession>(`/browser/open/${applicationId}`, payload ?? {}),

  getSession: (sessionId: string) =>
    api.get<BrowserSession>(`/browser/session/${sessionId}`),

  closeSession: (sessionId: string) =>
    api.delete<void>(`/browser/session/${sessionId}`),

  listSessions: () =>
    api.get<BrowserSessionListResponse>('/browser/sessions'),

  restartSession: (sessionId: string, payload?: { browser_type?: BrowserType }) =>
    api.post<BrowserSession>(`/browser/session/${sessionId}/restart`, payload ?? {}),

  getStatus: () =>
    api.get<BrowserStatusSummary>('/browser/status'),

  detectFormFields: (sessionId: string) =>
    api.post<FormDetectionResponse>(`/browser/forms/detect/${sessionId}`),

  fillFormFields: (sessionId: string, payload?: { overrides?: Record<string, string>; traverse_steps?: boolean }) =>
    api.post<FormFillResponse>(`/browser/forms/fill/${sessionId}`, payload ?? {}),

  getFormReport: (sessionId: string) =>
    api.get<FormFillResponse>(`/browser/forms/report/${sessionId}`),

  detectUploadFields: (sessionId: string) =>
    api.post<UploadDetectionResponse>(`/browser/uploads/detect/${sessionId}`),

  uploadResume: (
    sessionId: string,
    payload: { application_id: number; use_tailored_resume?: boolean; force_redetect?: boolean },
  ) => api.post<UploadStatusResponse>(`/browser/uploads/resume/${sessionId}`, payload),

  uploadCoverLetter: (
    sessionId: string,
    payload: { application_id: number; use_tailored_resume?: boolean; force_redetect?: boolean },
  ) => api.post<UploadStatusResponse>(`/browser/uploads/cover-letter/${sessionId}`, payload),

  uploadAll: (
    sessionId: string,
    payload: { application_id: number; use_tailored_resume?: boolean; force_redetect?: boolean },
  ) => api.post<UploadStatusResponse>(`/browser/uploads/all/${sessionId}`, payload),

  getUploadStatus: (sessionId: string, applicationId: number) =>
    api.get<UploadStatusResponse>(`/browser/uploads/status/${sessionId}`, { params: { application_id: applicationId } }),

  retryUpload: (
    sessionId: string,
    payload: { application_id: number; include_resume?: boolean; include_cover_letter?: boolean },
  ) => api.post<UploadStatusResponse>(`/browser/uploads/retry/${sessionId}`, payload),

  getReview: (sessionId: string) =>
    api.get<BrowserReviewReport>(`/browser/review/${sessionId}`),

  validateReview: (sessionId: string) =>
    api.post<SubmissionValidationReport>(`/browser/review/validate/${sessionId}`),

  confirmReview: (
    sessionId: string,
    payload: { confirmed: boolean; attempt_submission?: boolean; review_time_seconds?: number },
  ) => api.post<BrowserReviewConfirmResponse>(`/browser/review/confirm/${sessionId}`, payload),

  getReviewHistory: (applicationId: number) =>
    api.get<SubmissionAuditHistoryResponse>(`/browser/review/history/${applicationId}`),
};
