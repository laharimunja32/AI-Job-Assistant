import api from './api';
import type { PaginatedResponse } from '@/types';

export interface SavedJob {
  id: number;
  job_id: number | null;
  job_title: string;
  company_name: string;
  salary: string | null;
  location: string | null;
  skills: string[];
  employment_type: string | null;
  experience: string | null;
  posted_date: string | null;
  job_url: string | null;
  company_logo: string | null;
  description_preview: string | null;
  saved_at: string;
  is_saved: boolean;
}

export interface SavedJobCreate {
  job_id?: number | null;
  job_title: string;
  company_name: string;
  salary?: string | null;
  location?: string | null;
  skills?: string[];
  employment_type?: string | null;
  experience?: string | null;
  posted_date?: string | null;
  job_url?: string | null;
  company_logo?: string | null;
  description_preview?: string | null;
}

export const savedJobsService = {
  save: (payload: SavedJobCreate) => api.post<SavedJob>('/saved-jobs', payload),
  remove: (id: number) => api.delete(`/saved-jobs/${id}`),
  list: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<SavedJob>>('/saved-jobs', { params }),
  checkStatus: (params: { job_id?: number; saved_job_id?: number }) =>
    api.get<{ job_id: number | null; saved_job_id: number | null; is_saved: boolean }>(
      '/saved-jobs/status/check',
      { params },
    ),
};
