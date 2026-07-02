import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import FormAssistantPage from '@/pages/browser/FormAssistantPage';

vi.mock('@/hooks', () => ({
  useBrowserSessions: () => ({
    data: {
      items: [
        {
          session_id: 'session-form-1',
          browser_type: 'chromium',
        },
      ],
    },
  }),
  useDetectFormFields: () => ({
    isPending: false,
    error: null,
    mutate: vi.fn(),
    data: {
      data: {
        session_id: 'session-form-1',
        page_url: 'https://example.com',
        total_fields: 1,
        fields: [
          {
            field_id: 'email-1',
            field_type: 'email',
            selector: "[name='email']",
            label: 'Email',
            placeholder: 'name@example.com',
            input_name: 'email',
            input_type: 'email',
            required: true,
            confidence: 0.95,
            value: null,
          },
        ],
      },
    },
  }),
  useFillFormFields: () => ({
    isPending: false,
    error: null,
    mutate: vi.fn(),
    data: {
      data: {
        completion_percentage: 100,
        filled_fields: [{ field_id: 'email-1' }],
        unknown_fields: [],
        required_manual_input: [],
      },
    },
  }),
  useFormFillReport: () => ({
    data: null,
    error: null,
  }),
}));

describe('FormAssistantPage', () => {
  it('renders form assistant controls and detected rows', () => {
    render(<FormAssistantPage />);
    expect(screen.getByText('Form Assistant')).toBeInTheDocument();
    expect(screen.getAllByText('Detected Fields').length).toBeGreaterThan(0);
    expect(screen.getByText('email')).toBeInTheDocument();
    expect(screen.getByText('Auto Fill')).toBeInTheDocument();
  });
});
