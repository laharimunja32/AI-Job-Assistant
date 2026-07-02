import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useApplications } from '@/hooks/useApplications';
import { applicationsService } from '@/services';

vi.mock('@/services', () => ({
  applicationsService: {
    list: vi.fn(),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useApplications', () => {
  it('fetches application list with pagination', async () => {
    vi.mocked(applicationsService.list).mockResolvedValue({
      data: {
        items: [
          {
            id: 1,
            user_id: 1,
            job_id: 3,
            company_name: 'Acme',
            job_title: 'Backend Engineer',
            apply_url: 'https://acme.test/jobs/3',
            status: 'ready_to_apply',
            source: 'jobs',
            applied_date: null,
            selected_resume_id: 2,
            selected_tailored_resume_id: null,
            selected_cover_letter_id: null,
            notes: null,
            tags: ['python'],
            priority: 3,
            is_favorite: false,
            follow_up_date: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        total: 1,
        page: 1,
        size: 10,
      },
    } as never);

    const { result } = renderHook(() => useApplications({ page: 1, size: 10 }), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items[0].job_title).toBe('Backend Engineer');
  });
});
