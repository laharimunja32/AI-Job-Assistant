import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useWalkIns } from '@/hooks';
import { useQuery } from '@tanstack/react-query';
import { walkInsService } from '@/services';
import { WalkInCard } from '@/components/walk-ins/WalkInCard';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Button } from '@/components/ui/Button';
import { parseApiError } from '@/utils';

export default function WalkInsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = searchParams.get('tab') ?? 'all';
  const page = Number(searchParams.get('page') ?? 1);
  const [company, setCompany] = useState(searchParams.get('company') ?? '');
  const [city, setCity] = useState(searchParams.get('city') ?? '');

  const listQuery = useWalkIns({
    company: company || undefined,
    city: city || undefined,
    page,
    size: 12,
  });

  const todayQuery = useQuery({
    queryKey: ['walk-ins', 'today', page],
    queryFn: async () => {
      const { data } = await walkInsService.getToday({ page, size: 12 });
      return data;
    },
    enabled: tab === 'today',
  });

  const upcomingQuery = useQuery({
    queryKey: ['walk-ins', 'upcoming', page],
    queryFn: async () => {
      const { data } = await walkInsService.getUpcoming({ page, size: 12 });
      return data;
    },
    enabled: tab === 'upcoming',
  });

  const activeQuery = tab === 'today' ? todayQuery : tab === 'upcoming' ? upcomingQuery : listQuery;
  const { data, isLoading, error, refetch } = activeQuery;

  const setTab = (t: string) => {
    setSearchParams((p) => {
      const n = new URLSearchParams(p);
      n.set('tab', t);
      n.set('page', '1');
      return n;
    });
  };

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Walk-in Drives</h1>
        <p className="mt-1 text-sm text-slate-500">Discover on-site recruitment events near you</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(['all', 'today', 'upcoming'] as const).map((t) => (
          <Button key={t} variant={tab === t ? 'primary' : 'outline'} size="sm" onClick={() => setTab(t)}>
            {t === 'all' ? 'All' : t === 'today' ? "Today's" : 'Upcoming'}
          </Button>
        ))}
      </div>

      {tab === 'all' && (
        <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 sm:grid-cols-3">
          <Input label="Company" value={company} onChange={(e) => setCompany(e.target.value)} />
          <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} />
          <div className="flex items-end">
            <Button
              className="w-full"
              onClick={() =>
                setSearchParams((p) => {
                  const n = new URLSearchParams(p);
                  if (company) n.set('company', company);
                  if (city) n.set('city', city);
                  n.set('page', '1');
                  return n;
                })
              }
            >
              Search
            </Button>
          </div>
        </div>
      )}

      {!data || data.items.length === 0 ? (
        <EmptyState title="No walk-ins found" description="Check back later for new drive announcements." />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((w) => (
              <WalkInCard key={w.id} walkIn={w} showAiBadge={tab !== 'all'} />
            ))}
          </div>
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
        </>
      )}
    </div>
  );
}
