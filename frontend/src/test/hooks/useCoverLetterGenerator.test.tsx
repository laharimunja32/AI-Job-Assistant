import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useCoverLetterDetail, useCoverLetterHistory } from '@/hooks/useCoverLetterGenerator';

vi.mock('@/services', () => ({
  coverLetterGeneratorService: {
    getById: vi.fn().mockResolvedValue({
      data: {
        id: 1,
        user_id: 1,
        resume_id: 2,
        job_title: 'Backend Engineer',
        company_name: 'Acme',
        job_description: 'Python role',
        template_name: 'professional',
        generated_letter: 'Dear Hiring Manager...',
        tone: 'professional',
        length: 'medium',
        created_at: '2026-01-01T00:00:00Z',
        updated_at: '2026-01-01T00:00:00Z',
      },
    }),
    getHistory: vi.fn().mockResolvedValue({
      data: {
        items: [
          {
            id: 1,
            resume_id: 2,
            job_title: 'Backend Engineer',
            company_name: 'Acme',
            template_name: 'professional',
            tone: 'professional',
            length: 'medium',
            created_at: '2026-01-01T00:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        size: 20,
      },
    }),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useCoverLetterGenerator', () => {
  it('loads cover letter detail', async () => {
    const { result } = renderHook(() => useCoverLetterDetail(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.job_title).toBe('Backend Engineer');
  });

  it('loads cover letter history', async () => {
    const { result } = renderHook(() => useCoverLetterHistory(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
  });
});
