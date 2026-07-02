import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import UploadAssistantPage from '@/pages/browser/UploadAssistantPage';

vi.mock('@/hooks', () => ({
  useBrowserSessions: () => ({
    data: { items: [{ session_id: 'session-1', browser_type: 'chromium' }] },
  }),
  useApplications: () => ({
    data: {
      items: [
        {
          id: 11,
          company_name: 'Acme',
          job_title: 'Developer',
          selected_resume_id: 1,
          selected_tailored_resume_id: 2,
          selected_cover_letter_id: 3,
        },
      ],
    },
  }),
  useDetectUploadFields: () => ({
    mutate: vi.fn(),
    isPending: false,
    error: null,
    data: { data: { total_fields: 2, fields: [] } },
  }),
  useUploadAllDocuments: () => ({
    mutate: vi.fn(),
    isPending: false,
    error: null,
    data: { data: { status: 'completed', uploaded_fields: [], failed_fields: [], pending_fields: [] } },
  }),
  useRetryUpload: () => ({
    mutate: vi.fn(),
    isPending: false,
    error: null,
    data: null,
  }),
  useUploadStatus: () => ({
    data: null,
    error: null,
  }),
}));

describe('UploadAssistantPage', () => {
  it('renders upload assistant sections', () => {
    render(<UploadAssistantPage />);
    expect(screen.getByText('Upload Assistant')).toBeInTheDocument();
    expect(screen.getByText('Detect Upload Fields')).toBeInTheDocument();
    expect(screen.getByText('Upload All')).toBeInTheDocument();
    expect(screen.getByText('Upload History')).toBeInTheDocument();
  });
});
