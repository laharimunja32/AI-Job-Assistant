import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCoverLetter } from '@/hooks/useCoverLetters';
import { coverLettersService } from '@/services';

vi.mock('@/services', () => ({
  coverLettersService: {
    getById: vi.fn(),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useCoverLetter', () => {
  it('fetches generated cover letter details', async () => {
    vi.mocked(coverLettersService.getById).mockResolvedValue({
      data: {
        id: 3,
        user_id: 1,
        job_id: 5,
        company_name: 'Acme',
        template_id: 1,
        resume_id: 1,
        tailored_resume_id: 1,
        match_id: 2,
        cover_letter_version: 1,
        status: 'completed',
        download_formats: ['pdf', 'docx', 'markdown', 'html'],
        analysis: {
          company_name: 'Acme',
          role: 'Backend Engineer',
          responsibilities: ['Build APIs'],
          required_skills: ['Python'],
          preferred_skills: ['AWS'],
          company_values: ['Ownership'],
          industry: 'Technology',
          keywords: ['Python'],
        },
        sections: {
          introduction: 'Dear Hiring Manager',
          role_interest: 'I am excited about the role',
          relevant_skills: ['Python'],
          relevant_projects: ['Talent Match Engine'],
          certifications: [],
          closing_paragraph: 'Thank you',
          professional_signature: 'Cover User',
        },
        markdown_content: '# Cover Letter',
        html_content: '<h1>Cover Letter</h1>',
        quality_score: 92,
        generated_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    } as never);

    const { result } = renderHook(() => useCoverLetter(3, true), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.quality_score).toBe(92);
  });
});
