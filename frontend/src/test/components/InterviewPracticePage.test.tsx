import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import InterviewPracticePage from '@/pages/interviews/InterviewPracticePage';

vi.mock('@/hooks', () => ({
  useInterviewPreparation: () => ({
    data: {
      id: 1,
      job_id: 2,
      status: 'completed',
      questions: [{ id: 1, category: 'technical', question_text: 'Explain FastAPI', difficulty: 'medium', follow_up_questions: [], hints: [], sort_order: 0, preparation_id: 1, created_at: '' }],
    },
    isLoading: false,
  }),
  useStartInterview: () => ({
    isPending: false,
    mutate: (_id: number, options: { onSuccess: (value: { data: { current_question: { id: number; category: string; question_text: string; difficulty: string; follow_up_questions: string[]; hints: string[]; sort_order: number; preparation_id: number; created_at: string }; progress: { current_index: number; total_questions: number; questions_answered: number; percent_complete: number } } }) => void }) =>
      options.onSuccess({
        data: {
          current_question: {
            id: 1,
            category: 'technical',
            question_text: 'Explain FastAPI',
            difficulty: 'medium',
            follow_up_questions: [],
            hints: [],
            sort_order: 0,
            preparation_id: 1,
            created_at: '',
          },
          progress: { current_index: 0, total_questions: 1, questions_answered: 0, percent_complete: 0 },
        },
      }),
  }),
  useSubmitInterviewAnswer: () => ({ isPending: false, mutate: vi.fn() }),
  useFinishInterview: () => ({ isPending: false, mutate: vi.fn() }),
}));

vi.mock('@/contexts/ToastContext', () => ({
  useToast: () => ({ addToast: vi.fn() }),
}));

describe('InterviewPracticePage', () => {
  it('renders mock interview question', async () => {
    render(
      <MemoryRouter initialEntries={['/interview-prep/1/practice']}>
        <Routes>
          <Route path="/interview-prep/:preparationId/practice" element={<InterviewPracticePage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText('Mock Interview')).toBeInTheDocument();
    expect(screen.getByText('Explain FastAPI')).toBeInTheDocument();
  });
});
