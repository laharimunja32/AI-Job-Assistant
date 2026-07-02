import { useQuery, useMutation } from '@tanstack/react-query';
import { matchesService } from '@/services';

export const matchKeys = {
  all: ['matches'] as const,
  job: (jobId: number) => [...matchKeys.all, 'job', jobId] as const,
  history: (params?: { min_score?: number; page?: number; size?: number }) =>
    [...matchKeys.all, 'history', params] as const,
};

export function useMatchJob(jobId: number, enabled = true) {
  return useQuery({
    queryKey: matchKeys.job(jobId),
    queryFn: async () => {
      const { data } = await matchesService.matchJob(jobId);
      return data;
    },
    enabled: enabled && jobId > 0,
    staleTime: 5 * 60_000,
    retry: 1,
  });
}

export function useMatchHistory(params?: { min_score?: number; page?: number; size?: number }) {
  return useQuery({
    queryKey: matchKeys.history(params),
    queryFn: async () => {
      const { data } = await matchesService.getHistory(params);
      return data;
    },
  });
}

export function useRecalculateMatch() {
  return useMutation({
    mutationFn: (matchId: number) => matchesService.recalculate(matchId),
  });
}
