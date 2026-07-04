import { useState } from 'react';
import { Link } from 'react-router-dom';
import { HistoryTable } from '@/components/cover-letter-generator';
import { useCoverLetterHistory } from '@/hooks/useCoverLetterGenerator';
import { Pagination } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';

export default function CoverLetterHistoryPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useCoverLetterHistory(page, 10);

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Cover Letter History</h1>
          <p className="text-sm text-slate-500">Previously generated cover letters.</p>
        </div>
        <Link to="/cover-letter-generator" className="text-sm font-medium text-brand-600 hover:underline">
          Generate New
        </Link>
      </div>

      {data && (
        <>
          <HistoryTable items={data.items} />
          {data.total > 0 && <Pagination page={page} total={data.total} size={10} onPageChange={setPage} />}
        </>
      )}
    </div>
  );
}
