import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ReviewAssistantPage from '@/pages/browser/ReviewAssistantPage';

vi.mock('@/contexts/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn() }),
}));

vi.mock('@/hooks', () => ({
  useBrowserSessions: () => ({ data: { items: [{ session_id: 'session-1', browser_type: 'chromium' }] } }),
  useApplications: () => ({ data: { items: [{ id: 1, company_name: 'Acme', job_title: 'Engineer' }] } }),
  useBrowserReview: () => ({ data: null, isFetching: false, refetch: vi.fn() }),
  useReviewHistory: () => ({ data: { items: [] }, refetch: vi.fn() }),
  useDetectFormFields: () => ({ mutate: vi.fn(), isPending: false }),
  useFillFormFields: () => ({ mutate: vi.fn(), isPending: false }),
  useUploadAllDocuments: () => ({ mutate: vi.fn(), isPending: false }),
  useValidateBrowserReview: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useConfirmBrowserReview: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

describe('ReviewAssistantPage', () => {
  it('renders guided review page actions', () => {
    render(<ReviewAssistantPage />);
    expect(screen.getByText('Guided Review')).toBeInTheDocument();
    expect(screen.getByText('Refresh Validation')).toBeInTheDocument();
    expect(screen.getByText('Confirm Review')).toBeInTheDocument();
    expect(screen.getByText('Proceed to Submission')).toBeInTheDocument();
  });
});
