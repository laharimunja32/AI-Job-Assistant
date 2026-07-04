import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useResumeOptimizationHistory } from '@/hooks';
import { Badge, Card, EmptyState, Pagination } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';
import { formatDate } from '@/utils';

export default function ResumeOptimizationHistoryPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useResumeOptimizationHistory(page, 10);

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Optimization History</h1>
          <p className="text-sm text-slate-500">Previous resume analyses and ATS scores.</p>
        </div>
        <Link to="/resume-optimizer" className="text-sm font-medium text-brand-600 hover:underline">
          New Analysis
        </Link>
      </div>

      {data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4">
            {data.items.map((item) => (
              <Link key={item.id} to={`/resume-optimizer/${item.id}`}>
                <Card className="flex flex-wrap items-center justify-between gap-4 p-4 transition-colors hover:border-brand-300 dark:hover:border-brand-700">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-slate-100">
                      {item.job_title ?? 'Untitled Role'}
                      {item.company_name ? ` at ${item.company_name}` : ''}
                    </p>
                    <p className="text-xs text-slate-500">Resume #{item.resume_id} · {formatDate(item.created_at)}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="info">ATS {Math.round(item.ats_score)}</Badge>
                    <Badge variant="success">Overall {Math.round(item.overall_score)}</Badge>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
          <Pagination page={page} total={data.total} size={10} onPageChange={setPage} />
        </>
      ) : (
        <EmptyState title="No optimizations yet" description="Run your first resume analysis against a job description." />
      )}
    </div>
  );
}
