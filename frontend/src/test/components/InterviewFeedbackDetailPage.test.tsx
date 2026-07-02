import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import InterviewFeedbackDetailPage from '@/pages/interview-feedback/InterviewFeedbackDetailPage';

const mockDelete = vi.fn();
const mockRefetch = vi.fn();
const mockNavigate = vi.fn();

const feedbackData = {
  id: 1,
  session_id: 10,
  preparation_id: 5,
  job_id: 2,
  company_name: 'Acme',
  job_title: 'Backend Engineer',
  overall_score: 81,
  readiness_score: 79,
  confidence_score: 76,
  technical_score: 84,
  communication_score: 78,
  behavioral_score: 75,
  grammar_score: 80,
  clarity_score: 79,
  problem_solving_score: 82,
  summary_feedback: 'Strong technical depth with room to improve behavioral examples.',
  strengths: ['Clear examples'],
  weaknesses: ['Add more metrics'],
  improvement_suggestions: ['Practice STAR answers'],
  missing_skills: ['Kubernetes'],
  important_topics: ['FastAPI'],
  practice_recommendations: ['Run another mock session'],
  recommended_resources: ['Company careers page'],
  topics_to_improve: ['behavioral'],
  score_breakdown: { technical: 84, behavioral: 75 },
  question_reviews: [
    {
      question_id: 1,
      question_text: 'Explain FastAPI',
      category: 'technical',
      difficulty: 'medium',
      answer_text: 'FastAPI is a modern Python web framework.',
      ai_score: 85,
      feedback: 'Good concise answer.',
      strengths: ['Clear structure'],
      improvements: ['Add performance details'],
      time_spent_seconds: 90,
    },
  ],
  created_at: '2026-01-01T00:00:00Z',
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('@/hooks', () => ({
  useInterviewFeedbackDetail: vi.fn(),
  useDeleteInterviewFeedback: () => ({
    mutate: mockDelete,
    isPending: false,
  }),
}));

vi.mock('@/components/interview-feedback/FeedbackRadarChart', () => ({
  FeedbackRadarChart: () => <div data-testid="feedback-radar-chart">Skill Radar</div>,
}));

vi.mock('@/components/interview-feedback/PerformanceBreakdown', () => ({
  PerformanceBreakdown: () => <div data-testid="performance-breakdown">Category Breakdown</div>,
}));

import { useInterviewFeedbackDetail } from '@/hooks';

function renderPage(feedbackId = '1') {
  return render(
    <MemoryRouter initialEntries={[`/interview-feedback/${feedbackId}`]}>
      <Routes>
        <Route path="/interview-feedback" element={<div>Feedback List</div>} />
        <Route path="/interview-feedback/:feedbackId" element={<InterviewFeedbackDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('InterviewFeedbackDetailPage', () => {
  it('renders score cards', async () => {
    vi.mocked(useInterviewFeedbackDetail).mockReturnValue({
      data: feedbackData,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    } as never);

    renderPage();
    expect(await screen.findByText('Overall')).toBeInTheDocument();
    expect(screen.getByText('81%')).toBeInTheDocument();
    expect(screen.getByText('84%')).toBeInTheDocument();
  });

  it('renders radar chart', async () => {
    vi.mocked(useInterviewFeedbackDetail).mockReturnValue({
      data: feedbackData,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    } as never);

    renderPage();
    expect(await screen.findByTestId('feedback-radar-chart')).toBeInTheDocument();
  });

  it('renders question review section', async () => {
    vi.mocked(useInterviewFeedbackDetail).mockReturnValue({
      data: feedbackData,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    } as never);

    renderPage();
    expect(await screen.findByText('Question Reviews')).toBeInTheDocument();
    expect(screen.getByText('Explain FastAPI')).toBeInTheDocument();
  });

  it('calls delete mutation when delete button is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(useInterviewFeedbackDetail).mockReturnValue({
      data: feedbackData,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    } as never);

    mockDelete.mockImplementation((_id: number, options: { onSuccess?: () => void }) => {
      options.onSuccess?.();
    });

    renderPage();
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(mockDelete).toHaveBeenCalledWith(1, expect.any(Object));
    expect(mockNavigate).toHaveBeenCalledWith('/interview-feedback');
  });
});
