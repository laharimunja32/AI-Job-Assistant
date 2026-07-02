import { Link } from 'react-router-dom';
import { FeedbackCard } from '@/components/interviews/FeedbackCard';
import { InterviewScoreCard } from '@/components/interviews/InterviewScoreCard';
import { TopicStrengthChart } from '@/components/interviews/TopicStrengthChart';
import { Button, EmptyState, PageLoader } from '@/components/ui';
import { useInterviewFeedback } from '@/hooks';
import { useParams } from 'react-router-dom';

export default function InterviewFeedbackPage() {
  const { preparationId } = useParams<{ preparationId: string }>();
  const id = Number(preparationId);
  const { data: feedback, isLoading, isError } = useInterviewFeedback(id, id > 0);

  if (isLoading) return <PageLoader />;
  if (isError || !feedback) {
    return <EmptyState title="Feedback not available" description="Complete a practice session to generate feedback." />;
  }

  const chartTopics = Object.entries(feedback.score_breakdown).map(([topic, score]) => ({ topic, score }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interview Feedback</h1>
          <p className="text-sm text-slate-500">AI-generated insights from your latest practice session.</p>
        </div>
        <Link to={`/interview-prep/${id}/practice`}>
          <Button variant="secondary">Practice Again</Button>
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <InterviewScoreCard label="Overall Score" score={feedback.overall_score} />
        <InterviewScoreCard label="Readiness" score={feedback.readiness_score} />
        <InterviewScoreCard label="Confidence" score={feedback.confidence_score} />
        <InterviewScoreCard label="Technical" score={feedback.technical_score} />
        <InterviewScoreCard label="Communication" score={feedback.communication_score} />
        <InterviewScoreCard label="Behavioral" score={feedback.behavioral_score} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <FeedbackCard title="Strengths" items={feedback.strengths} variant="strength" />
        <FeedbackCard title="Weaknesses" items={feedback.weaknesses} variant="weakness" />
        <FeedbackCard title="AI Suggestions" items={feedback.improvement_suggestions} />
        <FeedbackCard title="Recommended Resources" items={feedback.recommended_resources} />
        <FeedbackCard title="Topics to Improve" items={feedback.topics_to_improve} />
        <FeedbackCard title="Practice Recommendations" items={feedback.practice_recommendations} />
      </div>

      <TopicStrengthChart title="Confidence by Category" topics={chartTopics} />
    </div>
  );
}
