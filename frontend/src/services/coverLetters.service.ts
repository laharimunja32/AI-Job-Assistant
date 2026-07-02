import api from './api';
import type {
  CoverLetterGenerateResponse,
  CoverLetterGenerationHistoryItem,
  CoverLetterTemplate,
  CoverLetterTemplatePayload,
  GeneratedCoverLetter,
  PaginatedResponse,
} from '@/types';

export const coverLettersService = {
  generate: (jobId: number) => api.post<CoverLetterGenerateResponse>(`/cover-letters/generate/${jobId}`),
  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<CoverLetterGenerationHistoryItem>>('/cover-letters/history', { params }),
  getById: (id: number) => api.get<GeneratedCoverLetter>(`/cover-letters/${id}`),
  delete: (id: number) => api.delete(`/cover-letters/${id}`),
  download: (id: number, format: 'pdf' | 'docx' | 'markdown' | 'html' = 'pdf') =>
    api.get<Blob>(`/cover-letters/${id}/download`, { params: { format }, responseType: 'blob' }),
  listTemplates: () => api.get<CoverLetterTemplate[]>('/cover-letters/templates'),
  createTemplate: (payload: CoverLetterTemplatePayload) => api.post<CoverLetterTemplate>('/cover-letters/templates', payload),
  updateTemplate: (id: number, payload: Partial<CoverLetterTemplatePayload>) =>
    api.put<CoverLetterTemplate>(`/cover-letters/templates/${id}`, payload),
  deleteTemplate: (id: number) => api.delete(`/cover-letters/templates/${id}`),
};
