import { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useJobs } from '@/hooks';
import { dashboardService } from '@/services';
import { JobCard, JobListGrid } from '@/components/jobs/JobCard';
import { Input, Select } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { parseApiError } from '@/utils';
import { Button } from '@/components/ui/Button';

export default function JobsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [keyword, setKeyword] = useState(searchParams.get('keyword') ?? '');
  const [location, setLocation] = useState(searchParams.get('location') ?? '');
  const page = Number(searchParams.get('page') ?? 1);
  const workMode = searchParams.get('work_mode') ?? '';
  const filter = searchParams.get('filter') ?? '';
  const sort = searchParams.get('sort') ?? 'newest';

  const isHighMatch = filter === 'high-match';

  const listParams = useMemo(
    () => ({
      keyword: keyword || undefined,
      location: location || undefined,
      work_mode: workMode || undefined,
      page,
      size: 12,
    }),
    [keyword, location, workMode, page],
  );

  const jobsQuery = useJobs(listParams);

  const highMatchQuery = useQuery({
    queryKey: ['dashboard', 'high-matches', page],
    queryFn: async () => {
      const { data } = await dashboardService.getHighMatches({ page, size: 12 });
      return data;
    },
    enabled: isHighMatch,
  });

  const data = isHighMatch ? highMatchQuery.data : jobsQuery.data;
  const isLoading = isHighMatch ? highMatchQuery.isLoading : jobsQuery.isLoading;
  const error = isHighMatch ? highMatchQuery.error : jobsQuery.error;
  const refetch = isHighMatch ? highMatchQuery.refetch : jobsQuery.refetch;

  const items = isHighMatch
    ? (data?.items ?? [])
    : sort === 'newest'
      ? [...(data?.items ?? [])].sort(
          (a, b) =>
            new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
        )
      : (data?.items ?? []);

  const applyFilters = () => {
    const params = new URLSearchParams();
    if (keyword) params.set('keyword', keyword);
    if (location) params.set('location', location);
    if (workMode) params.set('work_mode', workMode);
    if (filter) params.set('filter', filter);
    if (sort) params.set('sort', sort);
    params.set('page', '1');
    setSearchParams(params);
  };

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Jobs</h1>
        <p className="mt-1 text-sm text-slate-500">
          {isHighMatch ? 'Jobs with 90%+ AI match score' : 'Browse all available positions'}
        </p>
      </div>

      {!isHighMatch && (
        <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:grid-cols-2 lg:grid-cols-5">
          <Input
            label="Keyword"
            placeholder="Title, skill..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <Input
            label="Location"
            placeholder="City, region..."
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <Select
            label="Work mode"
            value={workMode}
            onChange={(e) => setSearchParams((p) => { const n = new URLSearchParams(p); n.set('work_mode', e.target.value); return n; })}
            options={[
              { value: '', label: 'All modes' },
              { value: 'remote', label: 'Remote' },
              { value: 'hybrid', label: 'Hybrid' },
              { value: 'onsite', label: 'Onsite' },
            ]}
          />
          <Select
            label="Sort"
            value={sort}
            onChange={(e) => setSearchParams((p) => { const n = new URLSearchParams(p); n.set('sort', e.target.value); return n; })}
            options={[
              { value: 'newest', label: 'Newest first' },
              { value: 'default', label: 'Default' },
            ]}
          />
          <div className="flex items-end">
            <Button onClick={applyFilters} className="w-full">
              Apply filters
            </Button>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <EmptyState title="No jobs found" description="Try adjusting your filters or check back later." />
      ) : (
        <>
          <JobListGrid>
            {items.map((job) => (
              <JobCard
                key={job.id}
                job={{
                  ...job,
                  match_score: 'match_score' in job ? job.match_score : undefined,
                  match_category: 'match_category' in job ? job.match_category : undefined,
                  matched_skills: 'matched_skills' in job ? job.matched_skills : undefined,
                }}
                showMatch={isHighMatch}
              />
            ))}
          </JobListGrid>
          {data && (
            <Pagination
              page={data.page}
              size={data.size}
              total={data.total}
              onPageChange={(p) => {
                setSearchParams((prev) => {
                  const n = new URLSearchParams(prev);
                  n.set('page', String(p));
                  return n;
                });
              }}
            />
          )}
        </>
      )}
    </div>
  );
}
