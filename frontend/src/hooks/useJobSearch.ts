import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { jobSearchService, type LiveJobSearchParams } from '@/services/jobSearch.service';

export const jobSearchKeys = {
  all: ['job-search'] as const,
  search: (params: LiveJobSearchParams) => [...jobSearchKeys.all, 'search', params] as const,
  history: (limit?: number) => [...jobSearchKeys.all, 'history', limit] as const,
  detail: (id: number) => [...jobSearchKeys.all, 'detail', id] as const,
};

export function useJobSearch(params: LiveJobSearchParams, enabled = true) {
  return useQuery({
    queryKey: jobSearchKeys.search(params),
    queryFn: async () => (await jobSearchService.search(params)).data,
    enabled: enabled && Boolean(params.keyword || params.location || params.company),
    placeholderData: (prev) => prev,
  });
}

export function useJobSearchMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: LiveJobSearchParams) => jobSearchService.search(params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: jobSearchKeys.all }),
  });
}

export function useJobSearchHistory(limit = 20) {
  return useQuery({
    queryKey: jobSearchKeys.history(limit),
    queryFn: async () => (await jobSearchService.getHistory(limit)).data,
  });
}

export function useJobSearchDetail(id: number) {
  return useQuery({
    queryKey: jobSearchKeys.detail(id),
    queryFn: async () => (await jobSearchService.getById(id)).data,
    enabled: id > 0,
  });
}
