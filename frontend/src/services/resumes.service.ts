import api from './api';
import type { Resume, PaginatedResponse } from '@/types';

export interface ResumeListParams {
  page?: number;
  size?: number;
  active?: boolean;
  filename_contains?: string;
}

export const resumesService = {
  list: (params?: ResumeListParams) =>
    api.get<PaginatedResponse<Resume>>('/resumes', { params }),

  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Resume>('/resumes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  activate: (resumeId: number) =>
    api.post<Resume>(`/resumes/${resumeId}/activate`),

  delete: (resumeId: number) =>
    api.delete(`/resumes/${resumeId}`),

  download: (resumeId: number) =>
    api.get<Blob>(`/resumes/${resumeId}/download`, { responseType: 'blob' }),
};
