import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { resumesService, type ResumeListParams } from '@/services';

export const resumeKeys = {
  all: ['resumes'] as const,
  list: (params: ResumeListParams) => [...resumeKeys.all, 'list', params] as const,
};

export function useResumes(params: ResumeListParams = {}) {
  return useQuery({
    queryKey: resumeKeys.list(params),
    queryFn: async () => {
      const { data } = await resumesService.list(params);
      return data;
    },
  });
}

export function useUploadResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => resumesService.upload(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: resumeKeys.all }),
  });
}

export function useActivateResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => resumesService.activate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: resumeKeys.all }),
  });
}

export function useDeleteResume() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => resumesService.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: resumeKeys.all }),
  });
}
