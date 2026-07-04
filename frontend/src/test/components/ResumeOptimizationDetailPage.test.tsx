import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ResumeOptimizationDetailPage from '@/pages/resume-optimizer/ResumeOptimizationDetailPage';

vi.mock('@/hooks', () => ({
  useResumeOptimization: () => ({
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
      matched_keywords: ['Python'],
      missing_keywords: ['Kubernetes'],
      matched_skills: ['Python'],
      missing_skills: ['Terraform'],
      recommendations: ['Mirror job terminology in your summary.'],
      tailored_resume: '# Optimized Resume\n\n## Skills\n- Python',
      created_at: '2026-01-01T00:00:00Z',
    },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useDeleteResumeOptimization: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock('@/services', () => ({
  resumeOptimizerService: { download: vi.fn() },
}));

vi.mock('@/contexts/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn() }),
}));

describe('ResumeOptimizationDetailPage', () => {
  it('renders ATS score and recommendations', () => {
    render(
      <MemoryRouter initialEntries={['/resume-optimizer/1']}>
        <Routes>
          <Route path="/resume-optimizer/:id" element={<ResumeOptimizationDetailPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    expect(screen.getByText('Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Matched Skills')).toBeInTheDocument();
  });
});
