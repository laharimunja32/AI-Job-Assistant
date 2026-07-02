import api from './api';
import type { PaginatedResponse, ResumeGenerationHistoryItem, TailoredResume, TailoredResumeGenerateResponse } from '@/types';

export const resumeTailoringService = {
  generate: (jobId: number) =>
    api.post<TailoredResumeGenerateResponse>(`/resume-tailoring/generate/${jobId}`),

  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<ResumeGenerationHistoryItem>>('/resume-tailoring/history', { params }),

  getById: (id: number) =>
    api.get<TailoredResume>(`/resume-tailoring/${id}`),

  delete: (id: number) =>
    api.delete(`/resume-tailoring/${id}`),

  download: (id: number, format: 'pdf' | 'docx' | 'markdown' | 'html' = 'pdf') =>
    api.get<Blob>(`/resume-tailoring/${id}/download`, { params: { format }, responseType: 'blob' }),
};
