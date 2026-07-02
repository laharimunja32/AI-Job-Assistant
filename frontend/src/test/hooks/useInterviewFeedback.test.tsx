import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import {
  useDeleteInterviewFeedback,
  useEvaluateInterviewFeedback,
  useInterviewFeedbackDetail,
  useInterviewFeedbackHistory,
  useInterviewFeedbackProgress,
} from '@/hooks/useInterviewFeedback';

const mockAddToast = vi.fn();

vi.mock('@/contexts/ToastContext', () => ({
  useToast: () => ({ addToast: mockAddToast }),
}));

vi.mock('@/services', () => ({
  interviewFeedbackService: {
    evaluate: vi.fn().mockResolvedValue({
      data: {
        id: 1,
        session_id: 10,
        preparation_id: 5,
        overall_score: 81,
        created_at: '2026-01-01T00:00:00Z',
      },
    }),
    getHistory: vi.fn().mockResolvedValue({
      data: {
        items: [{ id: 1, session_id: 10, preparation_id: 5, job_title: 'Backend Engineer', created_at: '2026-01-01T00:00:00Z' }],
        total: 1,
        page: 1,
        size: 20,
      },
    }),
    getProgress: vi.fn().mockResolvedValue({
      data: {
        average_score: 78,
        best_score: 85,
        latest_score: 80,
        completed_interviews: 2,
        strongest_skill: 'technical',
        weakest_skill: 'behavioral',
        score_trend: [],
        skill_distribution: [],
        performance_breakdown: {},
      },
    }),
    getById: vi.fn().mockResolvedValue({
      data: {
        id: 1,
        session_id: 10,
        preparation_id: 5,
        overall_score: 81,
        strengths: [],
        weaknesses: [],
        improvement_suggestions: [],
        missing_skills: [],
        important_topics: [],
        practice_recommendations: [],
        recommended_resources: [],
        topics_to_improve: [],
        score_breakdown: {},
        question_reviews: [],
        created_at: '2026-01-01T00:00:00Z',
      },
    }),
    delete: vi.fn().mockResolvedValue({}),
  },
}));

import { interviewFeedbackService } from '@/services';

function wrapper({ children }: { children: React.ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe('useInterviewFeedback', () => {
  it('loads feedback history', async () => {
    const { result } = renderHook(() => useInterviewFeedbackHistory(1, 20), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.items).toHaveLength(1);
    expect(interviewFeedbackService.getHistory).toHaveBeenCalledWith(1, 20);
  });

  it('loads feedback progress', async () => {
    const { result } = renderHook(() => useInterviewFeedbackProgress(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.completed_interviews).toBe(2);
    expect(interviewFeedbackService.getProgress).toHaveBeenCalled();
  });

  it('loads feedback detail', async () => {
    const { result } = renderHook(() => useInterviewFeedbackDetail(1), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.id).toBe(1);
    expect(interviewFeedbackService.getById).toHaveBeenCalledWith(1);
  });

  it('evaluates interview feedback', async () => {
    const { result } = renderHook(() => useEvaluateInterviewFeedback(), { wrapper });
    await result.current.mutateAsync(10);
    expect(interviewFeedbackService.evaluate).toHaveBeenCalledWith(10);
    expect(mockAddToast).toHaveBeenCalledWith('Interview feedback evaluated successfully', 'success');
  });

  it('deletes interview feedback', async () => {
    const { result } = renderHook(() => useDeleteInterviewFeedback(), { wrapper });
    await result.current.mutateAsync(1);
    expect(interviewFeedbackService.delete).toHaveBeenCalledWith(1);
    expect(mockAddToast).toHaveBeenCalledWith('Interview feedback deleted successfully', 'success');
  });
});
