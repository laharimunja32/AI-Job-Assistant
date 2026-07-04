import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import CoverLetterDetailPage from '@/pages/cover-letter-generator/CoverLetterDetailPage';

vi.mock('@/hooks/useCoverLetterGenerator', () => ({
  useCoverLetterDetail: () => ({
    data: {
      id: 1,
      user_id: 1,
      resume_id: 2,
      job_title: 'Backend Engineer',
      company_name: 'Acme Corp',
      job_description: 'Python role',
      template_name: 'professional',
      generated_letter: 'Dear Hiring Manager, I am excited to apply...',
      tone: 'professional',
      length: 'medium',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useUpdateCoverLetter: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useDeleteCoverLetter: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

vi.mock('@/services', () => ({
  coverLetterGeneratorService: { download: vi.fn() },
}));

vi.mock('@/contexts/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn() }),
}));

describe('CoverLetterDetailPage', () => {
  it('renders cover letter detail', () => {
    render(
      <MemoryRouter initialEntries={['/cover-letter-generator/1']}>
        <Routes>
          <Route path="/cover-letter-generator/:id" element={<CoverLetterDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    expect(screen.getByText('Acme Corp')).toBeInTheDocument();
    expect(screen.getByText('Edit Cover Letter')).toBeInTheDocument();
    expect(screen.getByText('Preview')).toBeInTheDocument();
  });
});
