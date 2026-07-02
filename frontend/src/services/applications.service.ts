import api from './api';
import type { Application, ApplicationHistoryItem, PaginatedResponse } from '@/types';

export interface ApplicationListParams {
  page?: number;
  size?: number;
  status?: string;
  company?: string;
  job_title?: string;
  search?: string;
  favorites_only?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CreateApplicationPayload {
  job_id: number;
  company_name: string;
  job_title: string;
  apply_url?: string | null;
  selected_resume_id?: number | null;
  selected_tailored_resume_id?: number | null;
  selected_cover_letter_id?: number | null;
  status?: string;
  source?: string | null;
  notes?: string | null;
  tags?: string[];
  priority?: number;
  is_favorite?: boolean;
  follow_up_date?: string | null;
}

export type UpdateApplicationPayload = Partial<CreateApplicationPayload> & { applied_date?: string | null };

export const applicationsService = {
  list: (params?: ApplicationListParams) => api.get<PaginatedResponse<Application>>('/applications', { params }),
  getById: (id: number) => api.get<Application>(`/applications/${id}`),
  create: (payload: CreateApplicationPayload) => api.post<Application>('/applications', payload),
  update: (id: number, payload: UpdateApplicationPayload) => api.put<Application>(`/applications/${id}`, payload),
  remove: (id: number) => api.delete(`/applications/${id}`),
  updateFavorite: (id: number, is_favorite: boolean) => api.patch<Application>(`/applications/${id}/favorite`, { is_favorite }),
  updateNotes: (id: number, notes: string) => api.patch<Application>(`/applications/${id}/notes`, { notes }),
  updatePriority: (id: number, priority: number) => api.patch<Application>(`/applications/${id}/priority`, { priority }),
  getHistory: (id: number, page = 1, size = 20) =>
    api.get<PaginatedResponse<ApplicationHistoryItem>>(`/applications/${id}/history`, { params: { page, size } }),
};
