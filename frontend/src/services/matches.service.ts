import api from './api';
import type { Match, PaginatedResponse } from '@/types';

export const matchesService = {
  matchJob: (jobId: number) =>
    api.post<Match>(`/matches/jobs/${jobId}`),

  matchAll: () => api.post<Match[]>('/matches/jobs'),

  getHistory: (params?: { min_score?: number; page?: number; size?: number }) =>
    api.get<PaginatedResponse<Match>>('/matches', { params }),

  recalculate: (matchId: number) =>
    api.post<Match>(`/matches/${matchId}/recalculate`),

  delete: (matchId: number) =>
    api.delete(`/matches/${matchId}`),
};
