import { useQuery } from '@tanstack/react-query';
import { walkInsService, type WalkInSearchParams } from '@/services';

export const walkInKeys = {
  all: ['walk-ins'] as const,
  list: (params: WalkInSearchParams) => [...walkInKeys.all, 'list', params] as const,
  detail: (id: number) => [...walkInKeys.all, 'detail', id] as const,
};

export function useWalkIns(params: WalkInSearchParams) {
  return useQuery({
    queryKey: walkInKeys.list(params),
    queryFn: async () => {
      const { data } = await walkInsService.list(params);
      return data;
    },
    placeholderData: (prev) => prev,
  });
}

export function useWalkIn(id: number) {
  return useQuery({
    queryKey: walkInKeys.detail(id),
    queryFn: () => walkInsService.getById(id),
    enabled: id > 0,
  });
}
