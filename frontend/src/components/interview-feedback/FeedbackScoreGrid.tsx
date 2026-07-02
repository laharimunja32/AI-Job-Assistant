import { Card } from '@/components/ui';
import type { InterviewFeedbackDetail } from '@/types';

interface ScoreItem {
  label: string;
  score: number | null | undefined;
}

interface FeedbackScoreGridProps {
  feedback: Pick<
    InterviewFeedbackDetail,
    | 'overall_score'
    | 'readiness_score'
    | 'confidence_score'
    | 'technical_score'
    | 'communication_score'
    | 'behavioral_score'
    | 'grammar_score'
    | 'clarity_score'
    | 'problem_solving_score'
  >;
}

export function FeedbackScoreGrid({ feedback }: FeedbackScoreGridProps) {
  const scores: ScoreItem[] = [
    { label: 'Overall', score: feedback.overall_score },
    { label: 'Readiness', score: feedback.readiness_score },
    { label: 'Confidence', score: feedback.confidence_score },
    { label: 'Technical', score: feedback.technical_score },
    { label: 'Communication', score: feedback.communication_score },
    { label: 'Behavioral', score: feedback.behavioral_score },
    { label: 'Grammar', score: feedback.grammar_score },
    { label: 'Clarity', score: feedback.clarity_score },
    { label: 'Problem Solving', score: feedback.problem_solving_score },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {scores.map(({ label, score }) => (
        <Card key={label} className="p-4">
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-1 text-3xl font-bold text-slate-900 dark:text-slate-100">
            {score != null ? `${Math.round(score)}%` : '—'}
          </p>
        </Card>
      ))}
    </div>
  );
}
