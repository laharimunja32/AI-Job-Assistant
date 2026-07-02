import api from './api';
import type {
  InterviewAnswerSubmitResponse,
  InterviewFeedback,
  InterviewHistoryItem,
  InterviewPreparation,
  InterviewPreparationGenerateResponse,
  InterviewSessionFinishResponse,
  InterviewSessionStartResponse,
  InterviewStatistics,
  PaginatedResponse,
} from '@/types';

export const interviewsService = {
  generate: (jobId: number, applicationId?: number) =>
    api.post<InterviewPreparationGenerateResponse>(`/interviews/generate/${jobId}`, null, {
      params: applicationId ? { application_id: applicationId } : undefined,
    }),

  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<InterviewHistoryItem>>('/interviews/history', { params }),

  getById: (id: number) => api.get<InterviewPreparation>(`/interviews/${id}`),

  delete: (id: number) => api.delete(`/interviews/${id}`),

  start: (id: number) => api.post<InterviewSessionStartResponse>(`/interviews/${id}/start`),

  submitAnswer: (id: number, payload: { answer_text: string; time_spent_seconds?: number }) =>
    api.post<InterviewAnswerSubmitResponse>(`/interviews/${id}/answer`, payload),

  finish: (id: number) => api.post<InterviewSessionFinishResponse>(`/interviews/${id}/finish`),

  getFeedback: (id: number) => api.get<InterviewFeedback>(`/interviews/${id}/feedback`),

  getStatistics: () => api.get<InterviewStatistics>('/interviews/statistics'),
};
