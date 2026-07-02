import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { interviewsService } from '@/services';

export const interviewKeys = {
  all: ['interviews'] as const,
  detail: (id: number) => [...interviewKeys.all, 'detail', id] as const,
  history: (page?: number, size?: number) => [...interviewKeys.all, 'history', page, size] as const,
  feedback: (id: number) => [...interviewKeys.all, 'feedback', id] as const,
  statistics: () => [...interviewKeys.all, 'statistics'] as const,
};

export function useGenerateInterview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ jobId, applicationId }: { jobId: number; applicationId?: number }) =>
      interviewsService.generate(jobId, applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useInterviewPreparation(id: number, enabled = true, refetchInterval?: number | false) {
  return useQuery({
    queryKey: interviewKeys.detail(id),
    queryFn: async () => {
      const { data } = await interviewsService.getById(id);
      return data;
    },
    enabled: enabled && id > 0,
    refetchInterval: (query) => {
      if (refetchInterval !== undefined) return refetchInterval;
      const status = query.state.data?.status;
      return status === 'queued' || status === 'processing' ? 2000 : false;
    },
  });
}

export function useInterviewHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: interviewKeys.history(page, size),
    queryFn: async () => {
      const { data } = await interviewsService.getHistory({ page, size });
      return data;
    },
  });
}

export function useStartInterview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => interviewsService.start(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.detail(id) });
    },
  });
}

export function useSubmitInterviewAnswer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      answer_text,
      time_spent_seconds,
    }: {
      id: number;
      answer_text: string;
      time_spent_seconds?: number;
    }) => interviewsService.submitAnswer(id, { answer_text, time_spent_seconds }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.detail(variables.id) });
    },
  });
}

export function useFinishInterview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => interviewsService.finish(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.all });
      queryClient.invalidateQueries({ queryKey: interviewKeys.feedback(id) });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useInterviewFeedback(id: number, enabled = true) {
  return useQuery({
    queryKey: interviewKeys.feedback(id),
    queryFn: async () => {
      const { data } = await interviewsService.getFeedback(id);
      return data;
    },
    enabled: enabled && id > 0,
  });
}

export function useInterviewStatistics() {
  return useQuery({
    queryKey: interviewKeys.statistics(),
    queryFn: async () => {
      const { data } = await interviewsService.getStatistics();
      return data;
    },
    staleTime: 60_000,
  });
}

export function useDeleteInterviewPreparation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => interviewsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interviewKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
