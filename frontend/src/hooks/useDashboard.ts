import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dashboardService } from '@/services';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  full: (page?: number, size?: number) => [...dashboardKeys.all, 'full', page, size] as const,
  statistics: () => [...dashboardKeys.all, 'statistics'] as const,
  notifications: () => [...dashboardKeys.all, 'notifications'] as const,
};

export function useDashboard(page = 1, size = 10) {
  return useQuery({
    queryKey: dashboardKeys.full(page, size),
    queryFn: async () => {
      const { data } = await dashboardService.getFull({ page, size });
      return data;
    },
    staleTime: 60_000,
  });
}

export function useDashboardStatistics() {
  return useQuery({
    queryKey: dashboardKeys.statistics(),
    queryFn: async () => {
      const { data } = await dashboardService.getStatistics();
      return data;
    },
    staleTime: 60_000,
  });
}

export function useNotificationCandidates() {
  return useQuery({
    queryKey: dashboardKeys.notifications(),
    queryFn: async () => {
      const { data } = await dashboardService.getNotificationCandidates();
      return data;
    },
    staleTime: 30_000,
  });
}

export function useRefreshDashboard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => dashboardService.refresh(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
    },
  });
}
