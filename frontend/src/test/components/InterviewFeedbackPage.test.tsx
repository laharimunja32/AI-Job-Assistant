import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import InterviewFeedbackPage from '@/pages/interviews/InterviewFeedbackPage';

vi.mock('@/hooks', () => ({
  useInterviewFeedback: () => ({
    data: {
      id: 1,
      session_id: 2,
      preparation_id: 1,
      overall_score: 81,
      readiness_score: 79,
      confidence_score: 76,
      technical_score: 84,
      communication_score: 78,
      behavioral_score: 75,
      strengths: ['Clear examples'],
      weaknesses: ['Add more metrics'],
      improvement_suggestions: ['Practice STAR answers'],
      missing_skills: ['Kubernetes'],
      important_topics: ['FastAPI'],
      practice_recommendations: ['Run another mock session'],
      recommended_resources: ['Company careers page'],
      topics_to_improve: ['behavioral'],
      score_breakdown: { technical: 84, behavioral: 75 },
      created_at: '2026-01-01T00:00:00Z',
    },
    isLoading: false,
    isError: false,
  }),
}));

describe('InterviewFeedbackPage', () => {
  it('renders feedback scores and suggestions', async () => {
    render(
      <MemoryRouter initialEntries={['/interview-prep/1/feedback']}>
        <Routes>
          <Route path="/interview-prep/:preparationId/feedback" element={<InterviewFeedbackPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Interview Feedback')).toBeInTheDocument();
    expect(screen.getByText('Strengths')).toBeInTheDocument();
    expect(screen.getByText('Clear examples')).toBeInTheDocument();
    expect(screen.getByText('Practice STAR answers')).toBeInTheDocument();
  });
});
