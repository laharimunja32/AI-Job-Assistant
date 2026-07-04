import api from './api';
import type { PaginatedResponse } from '@/types';

export interface LiveJobResult {
  id: number | null;
  title: string;
  company: string;
  salary: string | null;
  location: string | null;
  skills: string[];
  employment_type: string | null;
  experience: string | null;
  posted_date: string | null;
  job_url: string | null;
  company_logo: string | null;
  description_preview: string | null;
  work_mode: string | null;
}

export interface LiveJobSearchParams {
  keyword?: string;
  location?: string;
  experience?: string;
  company?: string;
  salary?: string;
  remote?: boolean;
  hybrid?: boolean;
  onsite?: boolean;
  employment_type?: string;
  date_posted?: string;
  page?: number;
  size?: number;
}

export interface JobSearchHistoryItem {
  id: number;
  keyword: string | null;
  location: string | null;
  company: string | null;
  results_count: number;
  filters: Record<string, unknown>;
  created_at: string;
}

export const jobSearchService = {
  search: (payload: LiveJobSearchParams) =>
    api.post<PaginatedResponse<LiveJobResult>>('/job-search/search', payload),
  getHistory: (limit = 20) =>
    api.get<{ items: JobSearchHistoryItem[]; total: number }>('/job-search/history', { params: { limit } }),
  getById: (id: number) => api.get<JobSearchHistoryItem & { salary?: string; experience?: string }>(`/job-search/${id}`),
};
