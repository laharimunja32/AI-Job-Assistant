import { InterviewCard } from '@/components/interviews/InterviewCard';
import { EmptyState, PageLoader, Pagination } from '@/components/ui';
import { useInterviewHistory } from '@/hooks';
import { useState } from 'react';

export default function InterviewHistoryPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useInterviewHistory(page, 10);

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interview Practice History</h1>
        <p className="text-sm text-slate-500">Review past sessions, scores, and reopen feedback.</p>
      </div>

      {data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4">
            {data.items.map((item) => (
              <InterviewCard key={item.id} historyItem={item} />
            ))}
          </div>
          <Pagination page={page} total={data.total} size={10} onPageChange={setPage} />
        </>
      ) : (
        <EmptyState title="No practice sessions yet" description="Generate interview preparation from a job and complete a mock interview." />
      )}
    </div>
  );
}
