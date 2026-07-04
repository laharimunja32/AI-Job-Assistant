import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { coverLetterGeneratorService } from '@/services';

export const coverLetterGeneratorKeys = {
  all: ['cover-letter-generator'] as const,
  detail: (id: number) => [...coverLetterGeneratorKeys.all, 'detail', id] as const,
  history: (page?: number, size?: number) => [...coverLetterGeneratorKeys.all, 'history', page, size] as const,
};

export function useGenerateCoverLetter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      resume_id: number;
      job_description: string;
      job_title: string;
      company_name: string;
      template_name?: string;
      tone?: string;
      length?: string;
    }) => coverLetterGeneratorService.generate(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coverLetterGeneratorKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useCoverLetterHistory(page = 1, size = 20) {
  return useQuery({
    queryKey: coverLetterGeneratorKeys.history(page, size),
    queryFn: async () => {
      const { data } = await coverLetterGeneratorService.getHistory({ page, size });
      return data;
    },
  });
}

export function useCoverLetterDetail(id: number, enabled = true) {
  return useQuery({
    queryKey: coverLetterGeneratorKeys.detail(id),
    queryFn: async () => {
      const { data } = await coverLetterGeneratorService.getById(id);
      return data;
    },
    enabled: enabled && id > 0,
  });
}

export function useUpdateCoverLetter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, generated_letter }: { id: number; generated_letter: string }) =>
      coverLetterGeneratorService.update(id, generated_letter),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: coverLetterGeneratorKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: coverLetterGeneratorKeys.all });
    },
  });
}

export function useDeleteCoverLetter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => coverLetterGeneratorService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coverLetterGeneratorKeys.all });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
