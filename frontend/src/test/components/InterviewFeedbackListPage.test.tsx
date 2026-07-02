import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import InterviewFeedbackListPage from '@/pages/interview-feedback/InterviewFeedbackListPage';

const mockDelete = vi.fn();
const mockRefetchHistory = vi.fn();
const mockRefetchProgress = vi.fn();

const progressData = {
  average_score: 78,
  best_score: 85,
  latest_score: 80,
  completed_interviews: 2,
  strongest_skill: 'technical',
  weakest_skill: 'behavioral',
  score_trend: [{ feedback_id: 1, date: '2026-01-01T00:00:00Z', overall_score: 80 }],
  skill_distribution: [{ skill: 'technical', score: 82 }],
  performance_breakdown: { technical: 82, communication: 75 },
};

const historyData = {
  items: [
    {
      id: 1,
      session_id: 10,
      preparation_id: 5,
      job_id: 2,
      company_name: 'Acme',
      job_title: 'Backend Engineer',
      overall_score: 80,
      readiness_score: 78,
      confidence_score: 76,
      technical_score: 84,
      communication_score: 78,
      grammar_score: 80,
      clarity_score: 79,
      problem_solving_score: 81,
      created_at: '2026-01-01T00:00:00Z',
    },
  ],
  total: 1,
  page: 1,
  size: 10,
};

vi.mock('@/hooks', () => ({
  useInterviewFeedbackHistory: vi.fn(),
  useInterviewFeedbackProgress: vi.fn(),
  useDeleteInterviewFeedback: () => ({
    mutate: mockDelete,
    isPending: false,
  }),
}));

vi.mock('@/components/interview-feedback/FeedbackProgressChart', () => ({
  FeedbackProgressChart: () => <div data-testid="feedback-progress-chart" />,
}));

vi.mock('@/components/interview-feedback/SkillDistributionChart', () => ({
  SkillDistributionChart: () => <div data-testid="skill-distribution-chart" />,
}));

vi.mock('@/components/interview-feedback/PerformanceBreakdown', () => ({
  PerformanceBreakdown: () => <div data-testid="performance-breakdown" />,
}));

import { useInterviewFeedbackHistory, useInterviewFeedbackProgress } from '@/hooks';

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/interview-feedback']}>
      <Routes>
        <Route path="/interview-feedback" element={<InterviewFeedbackListPage />} />
        <Route path="/interview-feedback/:feedbackId" element={<div>Detail Page</div>} />
        <Route path="/interview-prep/history" element={<div>Interview Prep History</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('InterviewFeedbackListPage', () => {
  it('shows loading state', () => {
    vi.mocked(useInterviewFeedbackHistory).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      refetch: mockRefetchHistory,
    } as never);
    vi.mocked(useInterviewFeedbackProgress).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
      refetch: mockRefetchProgress,
    } as never);

    renderPage();
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('shows empty state when history has no items', () => {
    vi.mocked(useInterviewFeedbackHistory).mockReturnValue({
      data: { items: [], total: 0, page: 1, size: 10 },
      isLoading: false,
      error: null,
      refetch: mockRefetchHistory,
    } as never);
    vi.mocked(useInterviewFeedbackProgress).mockReturnValue({
      data: progressData,
      isLoading: false,
      error: null,
      refetch: mockRefetchProgress,
    } as never);

    renderPage();
    expect(screen.getByText('No feedback yet')).toBeInTheDocument();
  });

  it('renders feedback history', async () => {
    vi.mocked(useInterviewFeedbackHistory).mockReturnValue({
      data: historyData,
      isLoading: false,
      error: null,
      refetch: mockRefetchHistory,
    } as never);
    vi.mocked(useInterviewFeedbackProgress).mockReturnValue({
      data: progressData,
      isLoading: false,
      error: null,
      refetch: mockRefetchProgress,
    } as never);

    renderPage();
    expect(await screen.findByText('Backend Engineer')).toBeInTheDocument();
    expect(screen.getByText('Feedback History')).toBeInTheDocument();
  });

  it('calls delete mutation when delete button is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(useInterviewFeedbackHistory).mockReturnValue({
      data: historyData,
      isLoading: false,
      error: null,
      refetch: mockRefetchHistory,
    } as never);
    vi.mocked(useInterviewFeedbackProgress).mockReturnValue({
      data: progressData,
      isLoading: false,
      error: null,
      refetch: mockRefetchProgress,
    } as never);

    renderPage();
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(mockDelete).toHaveBeenCalledWith(1);
  });

  it('navigates to detail page from view details button', async () => {
    const user = userEvent.setup();
    vi.mocked(useInterviewFeedbackHistory).mockReturnValue({
      data: historyData,
      isLoading: false,
      error: null,
      refetch: mockRefetchHistory,
    } as never);
    vi.mocked(useInterviewFeedbackProgress).mockReturnValue({
      data: progressData,
      isLoading: false,
      error: null,
      refetch: mockRefetchProgress,
    } as never);

    renderPage();
    await user.click(screen.getByRole('link', { name: /view details/i }));
    expect(await screen.findByText('Detail Page')).toBeInTheDocument();
  });
});
