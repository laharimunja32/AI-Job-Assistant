import api from './api';
import type { PaginatedResponse, ResumeOptimization, ResumeOptimizationAnalyzeResponse, ResumeOptimizationHistoryItem } from '@/types';

export const resumeOptimizerService = {
  analyze: (payload: { resume_id: number; job_description: string; job_title?: string; company_name?: string }) =>
    api.post<ResumeOptimizationAnalyzeResponse>('/resume-optimizer/analyze', payload),

  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<ResumeOptimizationHistoryItem>>('/resume-optimizer/history', { params }),

  getById: (id: number) =>
    api.get<ResumeOptimization>(`/resume-optimizer/${id}`),

  delete: (id: number) =>
    api.delete(`/resume-optimizer/${id}`),

  download: (id: number, format: 'pdf' | 'docx' = 'pdf') =>
    api.get<Blob>(`/resume-optimizer/${id}/download`, { params: { format }, responseType: 'blob' }),
};
