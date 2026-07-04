import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useJobSearchHistory } from '@/hooks/useJobSearch';

vi.mock('@/services/jobSearch.service', () => ({
  jobSearchService: {
    getHistory: vi.fn().mockResolvedValue({
      data: { items: [{ id: 1, keyword: 'python', results_count: 2, created_at: '2026-07-01' }], total: 1 },
    }),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useJobSearchHistory', () => {
  it('loads search history', async () => {
    const { result } = renderHook(() => useJobSearchHistory(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.total).toBe(1);
  });
});
