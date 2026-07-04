import { useNavigate } from 'react-router-dom';
import { useSavedJobs, useRemoveSavedJob } from '@/hooks';
import { SavedJobCard } from '@/components/job-search';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Pagination } from '@/components/ui/Pagination';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';
import { useState } from 'react';
import type { SavedJob } from '@/services/savedJobs.service';

export default function SavedJobsPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, error, refetch } = useSavedJobs({ page, size: 12 });
  const removeMutation = useRemoveSavedJob();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleRemove = async (id: number) => {
    try {
      await removeMutation.mutateAsync(id);
      addToast('Removed from saved jobs', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleApply = (job: SavedJob) => {
    navigate('/browser-application', {
      state: {
        job_id: job.job_id,
        job_title: job.job_title,
        company_name: job.company_name,
        apply_url: job.job_url,
      },
    });
  };

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Saved Jobs</h1>
        <p className="mt-1 text-sm text-slate-500">Jobs you bookmarked for later</p>
      </div>

      {!data?.items.length ? (
        <EmptyState title="No saved jobs" description="Save jobs from live search to see them here." />
      ) : (
        <>
          <div className="grid gap-4">
            {data.items.map((job) => (
              <SavedJobCard key={job.id} job={job} onRemove={handleRemove} onApply={handleApply} />
            ))}
          </div>
          <Pagination
            page={page}
            total={data.total}
            size={12}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
