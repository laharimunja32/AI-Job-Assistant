import { Badge, Card } from '@/components/ui';
import type { QuestionReview } from '@/types';

interface QuestionReviewSectionProps {
  reviews: QuestionReview[];
}

const categoryLabels: Record<string, string> = {
  company_specific: 'Company',
  hr: 'HR',
  behavioral: 'Behavioral',
  technical: 'Technical',
  project: 'Project',
  resume_based: 'Resume',
};

function difficultyVariant(difficulty: string): 'success' | 'warning' | 'danger' | 'default' {
  if (difficulty === 'hard') return 'danger';
  if (difficulty === 'easy') return 'success';
  return 'warning';
}

export function QuestionReviewSection({ reviews }: QuestionReviewSectionProps) {
  if (reviews.length === 0) {
    return (
      <Card className="p-4">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Question Reviews</h3>
        <p className="mt-2 text-sm text-slate-500">No per-question reviews available.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Question Reviews</h3>
      {reviews.map((review, index) => (
        <Card key={review.question_id} className="p-5">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge variant="default">Question {index + 1}</Badge>
            <Badge variant="info">{categoryLabels[review.category] ?? review.category}</Badge>
            <Badge variant={difficultyVariant(review.difficulty)}>{review.difficulty}</Badge>
            {review.ai_score != null && <Badge variant="outline">{Math.round(review.ai_score)}% score</Badge>}
            {review.time_spent_seconds != null && (
              <Badge variant="outline">{review.time_spent_seconds}s spent</Badge>
            )}
          </div>

          <h4 className="text-base font-semibold text-slate-900 dark:text-slate-100">{review.question_text}</h4>

          {review.answer_text && (
            <div className="mt-3 rounded-lg bg-slate-50 p-3 dark:bg-slate-800/50">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Your answer</p>
              <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">{review.answer_text}</p>
            </div>
          )}

          {review.feedback && (
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{review.feedback}</p>
          )}

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-emerald-600 dark:text-emerald-400">
                Strengths
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
                {review.strengths.length > 0
                  ? review.strengths.map((item) => <li key={item}>{item}</li>)
                  : <li className="list-none pl-0 text-slate-500">None noted.</li>}
              </ul>
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-amber-600 dark:text-amber-400">
                Improvements
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
                {review.improvements.length > 0
                  ? review.improvements.map((item) => <li key={item}>{item}</li>)
                  : <li className="list-none pl-0 text-slate-500">None noted.</li>}
              </ul>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
