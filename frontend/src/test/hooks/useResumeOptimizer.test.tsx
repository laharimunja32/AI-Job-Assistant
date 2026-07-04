import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useResumeOptimization, useResumeOptimizationHistory } from '@/hooks/useResumeOptimizer';

vi.mock('@/services', () => ({
  resumeOptimizerService: {
    getById: vi.fn().mockResolvedValue({
      data: {
        id: 1,
        user_id: 1,
        resume_id: 2,
        job_title: 'Backend Engineer',
        company_name: 'Acme',
        ats_score: 88,
        overall_score: 87,
        keyword_match: 82,
        skill_match: 91,
        experience_match: 80,
        education_match: 100,
        matched_keywords: ['Python', 'FastAPI'],
        missing_keywords: ['Kubernetes'],
        matched_skills: ['Python', 'SQL'],
        missing_skills: ['Terraform'],
        recommendations: ['Add measurable outcomes to bullets.'],
        tailored_resume: '# Optimized Resume',
        created_at: '2026-01-01T00:00:00Z',
      },
    }),
    getHistory: vi.fn().mockResolvedValue({
      data: {
        items: [{ id: 1, resume_id: 2, job_title: 'Backend Engineer', company_name: 'Acme', ats_score: 88, overall_score: 87, created_at: '2026-01-01T00:00:00Z' }],
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

describe('useResumeOptimizer', () => {
  it('loads optimization detail', async () => {
    const { result } = renderHook(() => useResumeOptimization(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.ats_score).toBe(88);
  });

  it('loads optimization history', async () => {
    const { result } = renderHook(() => useResumeOptimizationHistory(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
  });
});
