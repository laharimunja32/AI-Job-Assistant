import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { savedJobsService, type SavedJobCreate } from '@/services/savedJobs.service';

export const savedJobsKeys = {
  all: ['saved-jobs'] as const,
  list: (params?: { page?: number; size?: number }) => [...savedJobsKeys.all, 'list', params] as const,
  status: (jobId?: number) => [...savedJobsKeys.all, 'status', jobId] as const,
};

export function useSavedJobs(params?: { page?: number; size?: number }) {
  return useQuery({
    queryKey: savedJobsKeys.list(params),
    queryFn: async () => (await savedJobsService.list(params)).data,
    placeholderData: (prev) => prev,
  });
}

export function useSaveJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SavedJobCreate) => savedJobsService.save(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: savedJobsKeys.all }),
  });
}

export function useRemoveSavedJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => savedJobsService.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: savedJobsKeys.all }),
  });
}

export function useSavedJobStatus(jobId?: number) {
  return useQuery({
    queryKey: savedJobsKeys.status(jobId),
    queryFn: async () => (await savedJobsService.checkStatus({ job_id: jobId })).data,
    enabled: jobId !== undefined && jobId > 0,
  });
}
