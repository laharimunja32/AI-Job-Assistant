import { useQuery } from '@tanstack/react-query';
import { jobsService, type JobSearchParams } from '@/services';

export const jobKeys = {
  all: ['jobs'] as const,
  list: (params: JobSearchParams) => [...jobKeys.all, 'list', params] as const,
  detail: (id: number) => [...jobKeys.all, 'detail', id] as const,
};

export function useJobs(params: JobSearchParams) {
  return useQuery({
    queryKey: jobKeys.list(params),
    queryFn: async () => {
      const { data } = await jobsService.listAll(params);
      return data;
    },
    placeholderData: (prev) => prev,
  });
}

export function useJob(id: number) {
  return useQuery({
    queryKey: jobKeys.detail(id),
    queryFn: () => jobsService.getById(id),
    enabled: id > 0,
  });
}
