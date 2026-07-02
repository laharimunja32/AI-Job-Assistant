import { useMemo } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { GenerationProgressIndicator } from '@/components/cover-letters/GenerationProgressIndicator';
import { InterviewCard } from '@/components/interviews/InterviewCard';
import { ReadinessGauge } from '@/components/interviews/ReadinessGauge';
import { Badge, Button, Card, EmptyState, PageLoader } from '@/components/ui';
import { useInterviewPreparation } from '@/hooks';
import { useJob } from '@/hooks/useJobs';

const categoryLabels: Record<string, string> = {
  company_specific: 'Company Specific',
  hr: 'HR',
  behavioral: 'Behavioral',
  technical: 'Technical',
  project: 'Project',
  resume_based: 'Resume Based',
};

export default function InterviewPreparationPage() {
  const { preparationId } = useParams<{ preparationId: string }>();
  const id = Number(preparationId);
  const navigate = useNavigate();
  const { data: preparation, isLoading, isError } = useInterviewPreparation(id, id > 0);
  const { data: job } = useJob(preparation?.job_id ?? 0);

  const categories = useMemo(() => {
    const counts = new Map<string, number>();
    preparation?.questions.forEach((question) => {
      counts.set(question.category, (counts.get(question.category) ?? 0) + 1);
    });
    return Array.from(counts.entries());
  }, [preparation?.questions]);

  if (isLoading) return <PageLoader />;
  if (isError || !preparation) {
    return <EmptyState title="Interview preparation not found" description="Generate a new preparation from a job detail page." />;
  }

  const generating = preparation.status === 'queued' || preparation.status === 'processing';

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interview Preparation</h1>
          <p className="text-slate-600 dark:text-slate-300">
            {job?.title ?? `Job #${preparation.job_id}`} · {job?.company ?? 'Company'}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/interview-prep/history">
            <Button variant="secondary">History</Button>
          </Link>
          {preparation.status === 'completed' && (
            <Button onClick={() => navigate(`/interview-prep/${id}/practice`)}>Start Practice</Button>
          )}
        </div>
      </div>

      {generating && <GenerationProgressIndicator status={preparation.status} />}

      <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
        <Card className="flex flex-col items-center gap-3 p-6">
          <ReadinessGauge score={preparation.readiness_score ?? 0} size="lg" />
          <Badge variant={preparation.status === 'completed' ? 'success' : 'warning'}>{preparation.status}</Badge>
          {preparation.estimated_duration_minutes && (
            <p className="text-sm text-slate-500">Estimated duration: {preparation.estimated_duration_minutes} min</p>
          )}
        </Card>

        <div className="space-y-4">
          <Card className="p-4">
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">Recommended Topics</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {preparation.recommended_topics.map((topic) => (
                <Badge key={topic} variant="info">{topic}</Badge>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">Question Categories</h2>
            <div className="mt-3 grid gap-2 sm:grid-cols-2">
              {categories.map(([category, count]) => (
                <div key={category} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                  <p className="text-sm font-medium">{categoryLabels[category] ?? category}</p>
                  <p className="text-xs text-slate-500">{count} questions</p>
                </div>
              ))}
            </div>
          </Card>

          <InterviewCard preparation={preparation} jobTitle={job?.title} companyName={job?.company ?? undefined} />
        </div>
      </div>
    </div>
  );
}
