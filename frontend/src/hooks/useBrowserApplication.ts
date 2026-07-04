import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  browserApplicationService,
  type BrowserApplicationStart,
} from '@/services/browserApplication.service';

export const browserApplicationKeys = {
  all: ['browser-application'] as const,
  history: (params?: { page?: number; size?: number }) =>
    [...browserApplicationKeys.all, 'history', params] as const,
  detail: (id: number) => [...browserApplicationKeys.all, 'detail', id] as const,
};

export function useBrowserApplicationHistory(params?: { page?: number; size?: number }) {
  return useQuery({
    queryKey: browserApplicationKeys.history(params),
    queryFn: async () => (await browserApplicationService.getHistory(params)).data,
    placeholderData: (prev) => prev,
  });
}

export function useBrowserApplication(id: number) {
  return useQuery({
    queryKey: browserApplicationKeys.detail(id),
    queryFn: async () => (await browserApplicationService.getById(id)).data,
    enabled: id > 0,
  });
}

export function useStartBrowserApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: BrowserApplicationStart) => browserApplicationService.start(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: browserApplicationKeys.all }),
  });
}

export function useSubmitBrowserApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, confirm = true }: { id: number; confirm?: boolean }) =>
      browserApplicationService.submit(id, { confirm }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: browserApplicationKeys.all }),
  });
}
