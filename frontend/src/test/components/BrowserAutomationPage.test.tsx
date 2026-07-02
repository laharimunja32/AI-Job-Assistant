import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import BrowserAutomationPage from '@/pages/browser/BrowserAutomationPage';

vi.mock('@/hooks', () => ({
  useBrowserSessions: () => ({
    isLoading: false,
    data: {
      total: 1,
      items: [
        {
          session_id: 'session-1',
          user_id: 1,
          application_id: 4,
          browser_type: 'firefox',
          status: 'active',
          current_url: 'https://example.com/jobs/4',
          started_time: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          screenshot_path: null,
          error_message: null,
          metadata: { title: 'Apply', final_url: 'https://example.com/jobs/4', redirected: false, navigation_time_ms: 1100 },
        },
      ],
    },
  }),
  useBrowserStatus: () => ({
    data: {
      active_sessions: 1,
      browser_status: 'healthy',
      navigation_success_rate: 100,
      last_browser_activity: new Date().toISOString(),
    },
  }),
  useCreateBrowserSession: () => ({ isPending: false, error: null, mutateAsync: vi.fn() }),
  useOpenApplicationInBrowser: () => ({ isPending: false, error: null, mutateAsync: vi.fn() }),
  useCloseBrowserSession: () => ({ isPending: false, error: null, mutate: vi.fn() }),
  useRestartBrowserSession: () => ({ isPending: false, error: null, mutate: vi.fn() }),
}));

describe('BrowserAutomationPage', () => {
  it('renders browser automation dashboard section', () => {
    render(<BrowserAutomationPage />);
    expect(screen.getByText('Browser Automation')).toBeInTheDocument();
    expect(screen.getByText('Active Sessions')).toBeInTheDocument();
    expect(screen.getByText('session-1')).toBeInTheDocument();
    expect(screen.getByText('Browser:')).toBeInTheDocument();
  });
});
