import { useQuery } from '@tanstack/react-query';
import { healthService } from '@/services';

export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await healthService.check();
      return data;
    },
    retry: 1,
    refetchInterval: 60_000,
  });
}
