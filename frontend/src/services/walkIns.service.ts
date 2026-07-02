import api from './api';
import type { WalkIn, PaginatedResponse } from '@/types';

export interface WalkInSearchParams {
  company?: string;
  role?: string;
  city?: string;
  eligibility?: string;
  walk_in_date?: string;
  page?: number;
  size?: number;
}

export const walkInsService = {
  list: (params?: WalkInSearchParams) =>
    api.get<PaginatedResponse<WalkIn>>('/walk-ins', { params }),

  getToday: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<WalkIn>>('/walk-ins/today', { params }),

  getUpcoming: (params?: { page?: number; size?: number }) =>
    api.get<PaginatedResponse<WalkIn>>('/walk-ins/upcoming', { params }),

  refresh: (params?: { keyword?: string; location?: string; eligibility?: string }) =>
    api.post<{ created: number; updated: number; total: number }>('/walk-ins/refresh', null, { params }),

  async getById(id: number): Promise<WalkIn | null> {
    let page = 1;
    const size = 100;
    while (page <= 10) {
      const { data } = await api.get<PaginatedResponse<WalkIn>>('/walk-ins', { params: { page, size } });
      const found = data.items.find((w) => w.id === id);
      if (found) return found;
      if (page * size >= data.total) break;
      page += 1;
    }
    return null;
  },
};
