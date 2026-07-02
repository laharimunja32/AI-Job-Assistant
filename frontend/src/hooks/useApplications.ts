import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { applicationsService, type ApplicationListParams, type CreateApplicationPayload, type UpdateApplicationPayload } from '@/services';

export const applicationKeys = {
  all: ['applications'] as const,
  list: (params: ApplicationListParams) => [...applicationKeys.all, 'list', params] as const,
  detail: (id: number) => [...applicationKeys.all, 'detail', id] as const,
  history: (id: number, page: number, size: number) => [...applicationKeys.all, 'history', id, page, size] as const,
};

export function useApplications(params: ApplicationListParams) {
  return useQuery({
    queryKey: applicationKeys.list(params),
    queryFn: async () => (await applicationsService.list(params)).data,
    placeholderData: (prev) => prev,
  });
}

export function useApplication(id: number, enabled = true) {
  return useQuery({
    queryKey: applicationKeys.detail(id),
    queryFn: async () => (await applicationsService.getById(id)).data,
    enabled: enabled && id > 0,
  });
}

export function useApplicationHistory(id: number, page = 1, size = 20, enabled = true) {
  return useQuery({
    queryKey: applicationKeys.history(id, page, size),
    queryFn: async () => (await applicationsService.getHistory(id, page, size)).data,
    enabled: enabled && id > 0,
  });
}

export function useCreateApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateApplicationPayload) => applicationsService.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: applicationKeys.all }),
  });
}

export function useUpdateApplication(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UpdateApplicationPayload) => applicationsService.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: applicationKeys.all }),
  });
}

export function useDeleteApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => applicationsService.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: applicationKeys.all }),
  });
}

export function useUpdateApplicationFavorite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_favorite }: { id: number; is_favorite: boolean }) =>
      applicationsService.updateFavorite(id, is_favorite),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: applicationKeys.all }),
  });
}
