import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { coverLettersService } from '@/services';

export const coverLetterKeys = {
  all: ['cover-letters'] as const,
  detail: (id: number) => [...coverLetterKeys.all, 'detail', id] as const,
  history: (page?: number, size?: number) => [...coverLetterKeys.all, 'history', page, size] as const,
  templates: () => [...coverLetterKeys.all, 'templates'] as const,
};

export function useGenerateJobCoverLetter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (jobId: number) => coverLettersService.generate(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coverLetterKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useCoverLetter(id: number, enabled = true, refetchInterval?: number | false) {
  return useQuery({
    queryKey: coverLetterKeys.detail(id),
    queryFn: async () => (await coverLettersService.getById(id)).data,
    enabled: enabled && id > 0,
    refetchInterval,
  });
}

export function useJobCoverLetterHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: coverLetterKeys.history(page, size),
    queryFn: async () => (await coverLettersService.getHistory({ page, size })).data,
  });
}

export function useCoverLetterTemplates() {
  return useQuery({
    queryKey: coverLetterKeys.templates(),
    queryFn: async () => (await coverLettersService.listTemplates()).data,
  });
}
