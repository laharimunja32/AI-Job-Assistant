import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useSavedJobs } from '@/hooks/useSavedJobs';

vi.mock('@/services/savedJobs.service', () => ({
  savedJobsService: {
    list: vi.fn().mockResolvedValue({
      data: { items: [{ id: 1, job_title: 'Engineer', company_name: 'Co', skills: [], is_saved: true, saved_at: '2026-07-01' }], total: 1, page: 1, size: 20 },
    }),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useSavedJobs', () => {
  it('loads saved jobs', async () => {
    const { result } = renderHook(() => useSavedJobs(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
  });
});
