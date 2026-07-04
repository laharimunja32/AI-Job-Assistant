import { useState } from 'react';
import { useBrowserApplicationHistory } from '@/hooks';
import { ApplicationHistoryTable, AutomationStatus } from '@/components/job-search';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState } from '@/components/ui/EmptyState';
import { Pagination } from '@/components/ui/Pagination';
import { parseApiError } from '@/utils';
import type { BrowserApplication } from '@/services/browserApplication.service';

export default function ApplicationHistoryPage() {
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<BrowserApplication | null>(null);
  const { data, isLoading, error, refetch } = useBrowserApplicationHistory({ page, size: 20 });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Application History</h1>
        <p className="mt-1 text-sm text-slate-500">Browser-assisted application automation history</p>
      </div>

      <ApplicationHistoryTable items={data?.items ?? []} onSelect={setSelected} />

      {data && data.total > 20 && (
        <Pagination page={page} total={data.total} size={20} onPageChange={setPage} />
      )}

      {selected && <AutomationStatus application={selected} />}
    </div>
  );
}
