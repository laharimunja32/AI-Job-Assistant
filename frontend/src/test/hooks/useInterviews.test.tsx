import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useInterviewHistory, useInterviewStatistics } from '@/hooks/useInterviews';

vi.mock('@/services', () => ({
  interviewsService: {
    getHistory: vi.fn().mockResolvedValue({
      data: {
        items: [{ id: 1, preparation_id: 10, job_id: 2, job_title: 'Backend Engineer', company_name: 'Acme', questions_answered: 6 }],
        total: 1,
        page: 1,
        size: 20,
      },
    }),
    getStatistics: vi.fn().mockResolvedValue({
      data: {
        total_preparations: 2,
        completed_preparations: 2,
        practice_sessions: 1,
        questions_answered: 6,
        average_readiness: 78,
        average_confidence: 74,
        strongest_topics: [{ topic: 'technical', score: 82 }],
        weakest_topics: [{ topic: 'behavioral', score: 68 }],
        category_breakdown: { technical: 82, behavioral: 68 },
      },
    }),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useInterviews', () => {
  it('loads interview history', async () => {
    const { result } = renderHook(() => useInterviewHistory(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
  });

  it('loads interview statistics', async () => {
    const { result } = renderHook(() => useInterviewStatistics(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.practice_sessions).toBe(1);
  });
});
