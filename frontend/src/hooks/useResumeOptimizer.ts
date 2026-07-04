import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { resumeOptimizerService } from '@/services';

export const resumeOptimizerKeys = {
  all: ['resume-optimizer'] as const,
  detail: (id: number) => [...resumeOptimizerKeys.all, 'detail', id] as const,
  history: (page?: number, size?: number) => [...resumeOptimizerKeys.all, 'history', page, size] as const,
};

export function useAnalyzeResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { resume_id: number; job_description: string; job_title?: string; company_name?: string }) =>
      resumeOptimizerService.analyze(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: resumeOptimizerKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useResumeOptimization(id: number, enabled = true) {
  return useQuery({
    queryKey: resumeOptimizerKeys.detail(id),
    queryFn: async () => {
      const { data } = await resumeOptimizerService.getById(id);
      return data;
    },
    enabled: enabled && id > 0,
  });
}

export function useResumeOptimizationHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: resumeOptimizerKeys.history(page, size),
    queryFn: async () => {
      const { data } = await resumeOptimizerService.getHistory({ page, size });
      return data;
    },
  });
}

export function useDeleteResumeOptimization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => resumeOptimizerService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: resumeOptimizerKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
