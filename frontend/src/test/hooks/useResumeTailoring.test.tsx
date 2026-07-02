import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTailoredResume } from '@/hooks/useResumeTailoring';
import { resumeTailoringService } from '@/services';

vi.mock('@/services', () => ({
  resumeTailoringService: {
    getById: vi.fn(),
  },
}));

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useTailoredResume', () => {
  it('fetches tailored resume details', async () => {
    vi.mocked(resumeTailoringService.getById).mockResolvedValue({
      data: {
        id: 11,
        user_id: 1,
        job_id: 5,
        template_id: 1,
        match_id: 2,
        resume_version: 1,
        status: 'completed',
        generated_at: new Date().toISOString(),
        ats_score: 88.5,
        analysis: {
          required_skills: ['Python'],
          preferred_skills: [],
          technologies: ['FastAPI'],
          experience: '2-4 years',
          keywords: ['Python'],
          responsibilities: ['Build APIs'],
          education: [],
          certifications: [],
        },
        improvements: {
          professional_summary: 'Strong backend engineer',
          skills_ordering: ['Python'],
          relevant_projects: [],
          relevant_certifications: [],
          achievements: [],
          keyword_optimization: [],
          ats_optimization: [],
        },
        markdown_content: '# Resume',
        html_content: '<h1>Resume</h1>',
        markdown_path: '/tmp/file.md',
        html_path: '/tmp/file.html',
        pdf_path: '/tmp/file.pdf',
        docx_path: '/tmp/file.docx',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    } as never);

    const { result } = renderHook(() => useTailoredResume(11, true), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.ats_score).toBe(88.5);
  });
});
