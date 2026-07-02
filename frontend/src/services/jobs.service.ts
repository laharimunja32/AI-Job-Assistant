import api from './api';
import type { Job, PaginatedResponse } from '@/types';

export interface JobSearchParams {
  keyword?: string;
  location?: string;
  work_mode?: string;
  employment_type?: string;
  page?: number;
  size?: number;
}

export const jobsService = {
  search: (params?: JobSearchParams) =>
    api.get<PaginatedResponse<Job>>('/jobs', { params }),

  listAll: (params?: Pick<JobSearchParams, 'keyword' | 'location' | 'page' | 'size'>) =>
    api.get<PaginatedResponse<Job>>('/jobs/all', { params }),

  async getById(id: number): Promise<Job | null> {
    let page = 1;
    const size = 100;
    while (page <= 10) {
      const { data } = await api.get<PaginatedResponse<Job>>('/jobs/all', { params: { page, size } });
      const found = data.items.find((j) => j.id === id);
      if (found) return found;
      if (page * size >= data.total) break;
      page += 1;
    }
    return null;
  },
};
