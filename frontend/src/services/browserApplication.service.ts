import api from './api';
import type { PaginatedResponse } from '@/types';

export interface BrowserApplication {
  id: number;
  application_id: number | null;
  job_id: number | null;
  company_name: string;
  job_title: string;
  status: string;
  browser_session_id: string | null;
  resume_id: number | null;
  cover_letter_id: number | null;
  duration_seconds: number | null;
  applied_date: string | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface BrowserApplicationStart {
  job_id?: number | null;
  job_title: string;
  company_name: string;
  apply_url?: string | null;
  resume_id?: number | null;
  cover_letter_id?: number | null;
  browser_type?: string | null;
}

export const browserApplicationService = {
  start: (payload: BrowserApplicationStart) =>
    api.post<BrowserApplication>('/browser-application/start', payload),
  submit: (id: number, payload: { confirm?: boolean; notes?: string }) =>
    api.post<BrowserApplication>(`/browser-application/${id}/submit`, payload),
  getHistory: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<BrowserApplication>>('/browser-application/history', { params }),
  getById: (id: number) => api.get<BrowserApplication>(`/browser-application/${id}`),
};
