import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useBrowserSessions, useFormFillReport } from '@/hooks/useBrowserAutomation';
import { browserService } from '@/services';

vi.mock('@/services', () => ({
  browserService: {
    listSessions: vi.fn(),
    getFormReport: vi.fn(),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useBrowserSessions', () => {
  it('returns browser sessions', async () => {
    vi.mocked(browserService.listSessions).mockResolvedValue({
      data: {
        total: 1,
        items: [
          {
            session_id: 'session-1',
            user_id: 1,
            application_id: 2,
            browser_type: 'chromium',
            status: 'active',
            current_url: 'https://example.com/apply',
            started_time: new Date().toISOString(),
            last_activity: new Date().toISOString(),
            screenshot_path: null,
            error_message: null,
          },
        ],
      },
    } as never);

    const { result } = renderHook(() => useBrowserSessions(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.total).toBe(1);
    expect(result.current.data?.items[0].browser_type).toBe('chromium');
  });
});

describe('useFormFillReport', () => {
  it('returns report for selected session', async () => {
    vi.mocked(browserService.getFormReport).mockResolvedValue({
      data: {
        session_id: 'session-1',
        page_url: 'https://example.com',
        completion_percentage: 75,
        filled_fields: [],
        skipped_fields: [],
        unknown_fields: [],
        required_manual_input: [],
        generated_at: new Date().toISOString(),
      },
    } as never);

    const { result } = renderHook(() => useFormFillReport('session-1'), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.session_id).toBe('session-1');
  });
});
