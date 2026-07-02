import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Trash2 } from 'lucide-react';
import { FeedbackCard } from '@/components/interviews/FeedbackCard';
import { FeedbackRadarChart } from '@/components/interview-feedback/FeedbackRadarChart';
import { FeedbackScoreGrid } from '@/components/interview-feedback/FeedbackScoreGrid';
import { PerformanceBreakdown } from '@/components/interview-feedback/PerformanceBreakdown';
import { QuestionReviewSection } from '@/components/interview-feedback/QuestionReviewSection';
import { Badge, Button, Card, EmptyState, ErrorState, PageLoader } from '@/components/ui';
import { useDeleteInterviewFeedback, useInterviewFeedbackDetail } from '@/hooks';
import { formatDateTime, parseApiError } from '@/utils';

export default function InterviewFeedbackDetailPage() {
  const { feedbackId } = useParams<{ feedbackId: string }>();
  const id = Number(feedbackId);
  const navigate = useNavigate();
  const { data: feedback, isLoading, error, refetch } = useInterviewFeedbackDetail(id, id > 0);
  const deleteMutation = useDeleteInterviewFeedback();

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  if (!feedback) {
    return <EmptyState title="Feedback not found" description="This feedback record may have been deleted." />;
  }

  const title = feedback.job_title ?? `Preparation #${feedback.preparation_id}`;
  const company = feedback.company_name ?? 'Company';
  const breakdown = Object.fromEntries(
    Object.entries(feedback.score_breakdown).filter(([, value]) => typeof value === 'number'),
  ) as Record<string, number>;

  const handleDelete = () => {
    deleteMutation.mutate(id, {
      onSuccess: () => navigate('/interview-feedback'),
    });
  };

  return (
    <div className="space-y-6">
      <Link
        to="/interview-feedback"
        className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline"
      >
        <ArrowLeft className="h-4 w-4" /> Back to feedback history
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{title}</h1>
          <p className="text-sm text-slate-500">{company}</p>
          <p className="mt-1 text-xs text-slate-500">Evaluated {formatDateTime(feedback.created_at)}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {feedback.overall_score != null && (
              <Badge variant="info">Overall {Math.round(feedback.overall_score)}%</Badge>
            )}
            <Badge variant="default">Session #{feedback.session_id}</Badge>
          </div>
        </div>
        <Button variant="outline" loading={deleteMutation.isPending} onClick={handleDelete}>
          <Trash2 className="h-4 w-4" /> Delete
        </Button>
      </div>

      {feedback.summary_feedback && (
        <Card className="p-4">
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Summary</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{feedback.summary_feedback}</p>
        </Card>
      )}

      <FeedbackScoreGrid feedback={feedback} />

      <div className="grid gap-4 lg:grid-cols-2">
        <FeedbackRadarChart feedback={feedback} />
        <PerformanceBreakdown title="Category Breakdown" breakdown={breakdown} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <FeedbackCard title="Strengths" items={feedback.strengths} variant="strength" />
        <FeedbackCard title="Weaknesses" items={feedback.weaknesses} variant="weakness" />
        <FeedbackCard title="AI Suggestions" items={feedback.improvement_suggestions} />
        <FeedbackCard title="Missing Skills" items={feedback.missing_skills} />
        <FeedbackCard title="Important Topics" items={feedback.important_topics} />
        <FeedbackCard title="Practice Recommendations" items={feedback.practice_recommendations} />
        <FeedbackCard title="Recommended Resources" items={feedback.recommended_resources} />
        <FeedbackCard title="Topics to Improve" items={feedback.topics_to_improve} />
      </div>

      <QuestionReviewSection reviews={feedback.question_reviews} />
    </div>
  );
}
