import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { resumeTailoringService } from '@/services';

export const resumeTailoringKeys = {
  all: ['resume-tailoring'] as const,
  detail: (id: number) => [...resumeTailoringKeys.all, 'detail', id] as const,
  history: (page?: number, size?: number) => [...resumeTailoringKeys.all, 'history', page, size] as const,
};

export function useGenerateTailoredResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (jobId: number) => resumeTailoringService.generate(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: resumeTailoringKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useTailoredResume(id: number, enabled = true, refetchInterval?: number | false) {
  return useQuery({
    queryKey: resumeTailoringKeys.detail(id),
    queryFn: async () => {
      const { data } = await resumeTailoringService.getById(id);
      return data;
    },
    enabled: enabled && id > 0,
    refetchInterval,
  });
}

export function useTailoredResumeHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: resumeTailoringKeys.history(page, size),
    queryFn: async () => {
      const { data } = await resumeTailoringService.getHistory({ page, size });
      return data;
    },
  });
}
