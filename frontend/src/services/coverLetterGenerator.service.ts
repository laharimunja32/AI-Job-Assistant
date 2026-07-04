import api from './api';
import type {
  CoverLetterGeneratorDetail,
  GenerateCoverLetterResponse,
  CoverLetterGeneratorHistoryItem,
  PaginatedResponse,
} from '@/types';

export const coverLetterGeneratorService = {
  generate: (payload: {
    resume_id: number;
    job_description: string;
    job_title: string;
    company_name: string;
    template_name?: string;
    tone?: string;
    length?: string;
  }) => api.post<GenerateCoverLetterResponse>('/cover-letter-generator/generate', payload),

  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<CoverLetterGeneratorHistoryItem>>('/cover-letter-generator/history', { params }),

  getById: (id: number) => api.get<CoverLetterGeneratorDetail>(`/cover-letter-generator/${id}`),

  update: (id: number, generated_letter: string) =>
    api.put<CoverLetterGeneratorDetail>(`/cover-letter-generator/${id}`, { generated_letter }),

  delete: (id: number) => api.delete(`/cover-letter-generator/${id}`),

  download: (id: number, format: 'pdf' | 'docx' = 'pdf') =>
    api.get<Blob>(`/cover-letter-generator/${id}/download`, { params: { format }, responseType: 'blob' }),
};
