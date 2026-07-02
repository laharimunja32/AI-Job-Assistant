import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { interviewFeedbackService } from '@/services';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';

export const interviewFeedbackKeys = {
  all: ['interview-feedback'] as const,
  history: (page?: number, size?: number) =>
    [...interviewFeedbackKeys.all, 'history', page, size] as const,
  progress: () => [...interviewFeedbackKeys.all, 'progress'] as const,
  detail: (feedbackId: number) => [...interviewFeedbackKeys.all, 'detail', feedbackId] as const,
};

export function useEvaluateInterviewFeedback() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  return useMutation({
    mutationFn: async (sessionId: number) => {
      const { data } = await interviewFeedbackService.evaluate(sessionId);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: interviewFeedbackKeys.all });
      queryClient.invalidateQueries({ queryKey: interviewFeedbackKeys.detail(data.id) });
      addToast('Interview feedback evaluated successfully', 'success');
    },
    onError: (err) => addToast(parseApiError(err), 'error'),
  });
}

export function useInterviewFeedbackHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: interviewFeedbackKeys.history(page, size),
    queryFn: async () => {
      const { data } = await interviewFeedbackService.getHistory(page, size);
      return data;
    },
  });
}

export function useInterviewFeedbackProgress() {
  return useQuery({
    queryKey: interviewFeedbackKeys.progress(),
    queryFn: async () => {
      const { data } = await interviewFeedbackService.getProgress();
      return data;
    },
    staleTime: 60_000,
  });
}

export function useInterviewFeedbackDetail(feedbackId: number, enabled = true) {
  return useQuery({
    queryKey: interviewFeedbackKeys.detail(feedbackId),
    queryFn: async () => {
      const { data } = await interviewFeedbackService.getById(feedbackId);
      return data;
    },
    enabled: enabled && feedbackId > 0,
  });
}

export function useDeleteInterviewFeedback() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();

  return useMutation({
    mutationFn: (feedbackId: number) => interviewFeedbackService.delete(feedbackId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: interviewFeedbackKeys.all });
      addToast('Interview feedback deleted successfully', 'success');
    },
    onError: (err) => addToast(parseApiError(err), 'error'),
  });
}
