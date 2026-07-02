import { Link, useNavigate } from 'react-router-dom';
import { BarChart2, Target, TrendingUp, Trophy, Users } from 'lucide-react';
import { DashboardSection } from '@/components/dashboard/DashboardSection';
import { StatCard } from '@/components/dashboard/StatCard';
import { Badge, Button, Card, EmptyState, ErrorState, PageLoader } from '@/components/ui';
import { useInterviewFeedbackHistory, useInterviewFeedbackProgress } from '@/hooks';
import { formatDate, parseApiError } from '@/utils';

export function InterviewFeedbackDashboardSection() {
  const navigate = useNavigate();
  const {
    data: progress,
    isLoading: progressLoading,
    error: progressError,
    refetch: refetchProgress,
  } = useInterviewFeedbackProgress();
  const {
    data: history,
    isLoading: historyLoading,
    error: historyError,
    refetch: refetchHistory,
  } = useInterviewFeedbackHistory(1, 5);

  const isLoading = progressLoading || historyLoading;
  const error = progressError ?? historyError;

  if (isLoading) return <PageLoader />;
  if (error) {
    return (
      <ErrorState
        message={parseApiError(error)}
        onRetry={() => {
          refetchProgress();
          refetchHistory();
        }}
      />
    );
  }

  const formatScore = (score: number | null | undefined) =>
    score != null ? `${Math.round(score)}%` : '—';

  const formatSkill = (skill: string | null | undefined) =>
    skill ? skill.replace(/_/g, ' ') : '—';

  return (
    <DashboardSection title="Interview Feedback" viewAllHref="/interview-feedback">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Average Interview Score"
          value={formatScore(progress?.average_score)}
          icon={<BarChart2 className="h-5 w-5" />}
          href="/interview-feedback"
        />
        <StatCard
          label="Best Score"
          value={formatScore(progress?.best_score)}
          icon={<Trophy className="h-5 w-5" />}
          href="/interview-feedback"
        />
        <StatCard
          label="Latest Score"
          value={formatScore(progress?.latest_score)}
          icon={<TrendingUp className="h-5 w-5" />}
          href="/interview-feedback"
        />
        <StatCard
          label="Completed Interviews"
          value={progress?.completed_interviews ?? 0}
          icon={<Users className="h-5 w-5" />}
          href="/interview-feedback"
        />
        <StatCard
          label="Strongest Skill"
          value={formatSkill(progress?.strongest_skill)}
          icon={<Target className="h-5 w-5" />}
          href="/interview-feedback"
        />
        <StatCard
          label="Weakest Skill"
          value={formatSkill(progress?.weakest_skill)}
          icon={<Target className="h-5 w-5" />}
          href="/interview-feedback"
        />
      </div>

      <div className="mt-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Recent Interview Feedback</h3>
        {history && history.items.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            {history.items.map((item) => (
              <Card key={item.id} className="p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-medium text-slate-900 dark:text-slate-100">
                      {item.job_title ?? `Preparation #${item.preparation_id}`}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">{formatDate(item.created_at)}</p>
                  </div>
                  {item.overall_score != null && (
                    <Badge variant="info">{Math.round(item.overall_score)}%</Badge>
                  )}
                </div>
                <div className="mt-4">
                  <Link to={`/interview-feedback/${item.id}`}>
                    <Button size="sm">View Feedback</Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No interview feedback yet"
            description="Complete a mock interview session to generate AI-powered feedback."
            actionLabel="Go to Interview Prep"
            onAction={() => navigate('/interview-prep/history')}
          />
        )}
      </div>
    </DashboardSection>
  );
}
