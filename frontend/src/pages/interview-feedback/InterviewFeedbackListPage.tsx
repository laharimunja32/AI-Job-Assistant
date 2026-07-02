import { Link, useNavigate } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import { useState } from 'react';
import { FeedbackProgressChart } from '@/components/interview-feedback/FeedbackProgressChart';
import { PerformanceBreakdown } from '@/components/interview-feedback/PerformanceBreakdown';
import { SkillDistributionChart } from '@/components/interview-feedback/SkillDistributionChart';
import { Badge, Button, Card, EmptyState, ErrorState, PageLoader, Pagination } from '@/components/ui';
import {
  useDeleteInterviewFeedback,
  useInterviewFeedbackHistory,
  useInterviewFeedbackProgress,
} from '@/hooks';
import type { InterviewFeedbackHistoryItem } from '@/types';
import { formatDateTime, parseApiError } from '@/utils';

function FeedbackHistoryCard({ item, onDelete }: { item: InterviewFeedbackHistoryItem; onDelete: (id: number) => void }) {
  const title = item.job_title ?? `Preparation #${item.preparation_id}`;
  const company = item.company_name ?? 'Company';

  return (
    <Card className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</p>
          <p className="text-sm text-slate-500">{company}</p>
          <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.created_at)}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {item.overall_score != null && <Badge variant="info">Overall {Math.round(item.overall_score)}%</Badge>}
            {item.readiness_score != null && <Badge variant="default">Readiness {Math.round(item.readiness_score)}%</Badge>}
            {item.technical_score != null && <Badge variant="default">Technical {Math.round(item.technical_score)}%</Badge>}
          </div>
        </div>
        {item.overall_score != null && (
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-100">{Math.round(item.overall_score)}%</p>
        )}
      </div>
      <div className="mt-4 flex gap-2">
        <Link to={`/interview-feedback/${item.id}`}>
          <Button size="sm">View Details</Button>
        </Link>
        <Button size="sm" variant="outline" onClick={() => onDelete(item.id)}>
          <Trash2 className="h-4 w-4" /> Delete
        </Button>
      </div>
    </Card>
  );
}

export default function InterviewFeedbackListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data: history, isLoading: historyLoading, error: historyError, refetch: refetchHistory } =
    useInterviewFeedbackHistory(page, 10);
  const { data: progress, isLoading: progressLoading, error: progressError, refetch: refetchProgress } =
    useInterviewFeedbackProgress();
  const deleteMutation = useDeleteInterviewFeedback();

  const isLoading = historyLoading || progressLoading;
  const error = historyError ?? progressError;

  if (isLoading) return <PageLoader />;
  if (error) {
    return (
      <ErrorState
        message={parseApiError(error)}
        onRetry={() => {
          refetchHistory();
          refetchProgress();
        }}
      />
    );
  }

  const handleDelete = (feedbackId: number) => {
    deleteMutation.mutate(feedbackId);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interview Feedback</h1>
        <p className="mt-1 text-sm text-slate-500">
          Track your interview performance, review AI evaluations, and monitor progress over time.
        </p>
      </div>

      {progress && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="p-4">
              <p className="text-xs text-slate-500">Average Score</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {progress.average_score != null ? `${Math.round(progress.average_score)}%` : '—'}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Best Score</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {progress.best_score != null ? `${Math.round(progress.best_score)}%` : '—'}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Latest Score</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {progress.latest_score != null ? `${Math.round(progress.latest_score)}%` : '—'}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs text-slate-500">Completed Interviews</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">{progress.completed_interviews}</p>
              {(progress.strongest_skill || progress.weakest_skill) && (
                <p className="mt-2 text-xs text-slate-500">
                  {progress.strongest_skill && <>Strongest: {progress.strongest_skill.replace(/_/g, ' ')}</>}
                  {progress.strongest_skill && progress.weakest_skill && ' · '}
                  {progress.weakest_skill && <>Weakest: {progress.weakest_skill.replace(/_/g, ' ')}</>}
                </p>
              )}
            </Card>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <FeedbackProgressChart trend={progress.score_trend} />
            <SkillDistributionChart distribution={progress.skill_distribution} />
          </div>

          <PerformanceBreakdown breakdown={progress.performance_breakdown} />
        </>
      )}

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Feedback History</h2>
        {history && history.items.length > 0 ? (
          <>
            <div className="grid gap-4">
              {history.items.map((item) => (
                <FeedbackHistoryCard key={item.id} item={item} onDelete={handleDelete} />
              ))}
            </div>
            <Pagination page={page} total={history.total} size={10} onPageChange={setPage} />
          </>
        ) : (
          <EmptyState
            title="No feedback yet"
            description="Complete a mock interview session to generate AI-powered feedback."
            actionLabel="View Interview Prep"
            onAction={() => navigate('/interview-prep/history')}
          />
        )}
      </div>
    </div>
  );
}
