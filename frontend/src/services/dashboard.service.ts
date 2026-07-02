import api from './api';
import type {
  DashboardResponse,
  DashboardStatistics,
  DashboardJobItem,
  DashboardWalkInItem,
  ClosingSoonItem,
  CityJobCount,
  RecentCompanyItem,
  NotificationCandidatesResponse,
  PaginatedResponse,
  AggregationRun,
} from '@/types';

export interface ListParams {
  page?: number;
  size?: number;
}

export const dashboardService = {
  getFull: (params?: ListParams) =>
    api.get<DashboardResponse>('/dashboard', { params }),

  getNewJobs: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/new-jobs', { params }),

  getRecommended: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/recommended', { params }),

  getHighMatches: (params?: ListParams & { min_score?: number }) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/high-matches', { params }),

  getWalkIns: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardWalkInItem>>('/dashboard/walk-ins', { params }),

  getTodaysWalkIns: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardWalkInItem>>('/dashboard/walk-ins/today', { params }),

  getUpcomingWalkIns: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardWalkInItem>>('/dashboard/walk-ins/upcoming', { params }),

  getClosingSoon: (params?: ListParams) =>
    api.get<PaginatedResponse<ClosingSoonItem>>('/dashboard/closing-soon', { params }),

  getRemoteJobs: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/remote', { params }),

  getHybridJobs: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/hybrid', { params }),

  getJobsByCity: () =>
    api.get<{ cities: CityJobCount[]; total_cities: number }>('/dashboard/jobs-by-city'),

  getRecentCompanies: (params?: ListParams) =>
    api.get<PaginatedResponse<RecentCompanyItem>>('/dashboard/recent-companies', { params }),

  getRecentlyUpdated: (params?: ListParams) =>
    api.get<PaginatedResponse<DashboardJobItem>>('/dashboard/recently-updated', { params }),

  getStatistics: () => api.get<DashboardStatistics>('/dashboard/statistics'),

  getNotificationCandidates: () =>
    api.get<NotificationCandidatesResponse>('/dashboard/notification-candidates'),

  refresh: () => api.post<{ matches_computed: number; high_matches: number; average_score: number }>('/dashboard/refresh'),

  triggerAggregation: () =>
    api.post<Record<string, unknown>>('/dashboard/aggregate'),

  getAggregationHistory: (params?: ListParams) =>
    api.get<PaginatedResponse<AggregationRun>>('/dashboard/aggregation/history', { params }),
};
