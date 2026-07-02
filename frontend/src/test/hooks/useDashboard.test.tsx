import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDashboard } from '@/hooks/useDashboard';
import { dashboardService } from '@/services';

vi.mock('@/services', () => ({
  dashboardService: {
    getFull: vi.fn(),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useDashboard', () => {
  beforeEach(() => {
    vi.mocked(dashboardService.getFull).mockResolvedValue({
      data: {
        new_jobs: { items: [], total: 0, page: 1, size: 10 },
        statistics: { total_active_jobs: 5 },
      },
    } as never);
  });

  it('fetches dashboard data', async () => {
    const { result } = renderHook(() => useDashboard(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.statistics.total_active_jobs).toBe(5);
  });
});
