import api from './api';
import type {
  InterviewFeedbackDetail,
  InterviewFeedbackHistoryResponse,
  InterviewFeedbackProgress,
} from '@/types';

export const interviewFeedbackService = {
  evaluate: (sessionId: number) =>
    api.post<InterviewFeedbackDetail>('/interview-feedback/evaluate', { session_id: sessionId }),

  getHistory: (page = 1, size = 20) =>
    api.get<InterviewFeedbackHistoryResponse>('/interview-feedback/history', {
      params: { page, size },
    }),

  getProgress: () => api.get<InterviewFeedbackProgress>('/interview-feedback/progress'),

  getById: (feedbackId: number) =>
    api.get<InterviewFeedbackDetail>(`/interview-feedback/${feedbackId}`),

  delete: (feedbackId: number) => api.delete(`/interview-feedback/${feedbackId}`),
};
