import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useApplications, useApplicationHistory, useDeleteApplication, useUpdateApplication, useUpdateApplicationFavorite } from '@/hooks';
import type { ApplicationStatus } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Pagination } from '@/components/ui/Pagination';
import { parseApiError, formatDate, formatDateTime } from '@/utils';
import { Star } from 'lucide-react';

const tabs: { key: ApplicationStatus | 'all'; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'draft', label: 'Draft' },
  { key: 'ready_to_apply', label: 'Ready to Apply' },
  { key: 'applied', label: 'Applied' },
  { key: 'assessment_received', label: 'Assessment' },
  { key: 'interview_scheduled', label: 'Interviews' },
  { key: 'offer_received', label: 'Offers' },
  { key: 'rejected', label: 'Rejected' },
];

const statusVariant: Record<ApplicationStatus, 'default' | 'info' | 'success' | 'warning' | 'danger'> = {
  draft: 'default',
  ready_to_apply: 'info',
  applied: 'info',
  assessment_received: 'warning',
  interview_scheduled: 'warning',
  technical_interview: 'warning',
  hr_interview: 'warning',
  offer_received: 'success',
  offer_accepted: 'success',
  offer_declined: 'danger',
  rejected: 'danger',
  withdrawn: 'default',
  ready_to_submit: 'info',
  review_required: 'warning',
  submitted: 'success',
  submission_failed: 'danger',
};

export default function ApplicationsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page') || '1');
  const status = searchParams.get('status') || '';
  const favoritesOnly = searchParams.get('favorites_only') === 'true';
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const { data, isLoading, error, refetch } = useApplications({
    page,
    size: 10,
    status: status || undefined,
    search: search || undefined,
    favorites_only: favoritesOnly || undefined,
    sort_by: 'updated_at',
    sort_order: 'desc',
  });
  const updateMutation = useUpdateApplication(selectedId ?? 0);
  const favoriteMutation = useUpdateApplicationFavorite();
  const deleteMutation = useDeleteApplication();
  const { data: history } = useApplicationHistory(selectedId ?? 0, 1, 10, Boolean(selectedId));

  const selected = useMemo(() => data?.items.find((item) => item.id === selectedId) ?? null, [data?.items, selectedId]);

  if (isLoading) {
    return <div className="text-sm text-slate-500">Loading applications...</div>;
  }

  if (error) {
    return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Applications</h1>
        <p className="mt-1 text-sm text-slate-500">
          Centralized application tracker with statuses, notes, priorities, and history.
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <Input
          placeholder="Search company or title"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
        <Select
          value={status}
          onChange={(event) => setSearchParams({ page: '1', status: event.target.value })}
          options={[
            { value: '', label: 'All statuses' },
            ...tabs.filter((t) => t.key !== 'all').map((t) => ({ value: t.key, label: t.label })),
          ]}
        />
        <Button
          variant={favoritesOnly ? 'primary' : 'outline'}
          onClick={() => setSearchParams({ page: '1', status, favorites_only: favoritesOnly ? 'false' : 'true' })}
        >
          Favorites only
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((t) => (
          <Button
            key={t.key}
            size="sm"
            variant={(status || 'all') === t.key ? 'primary' : 'outline'}
            onClick={() => setSearchParams({ page: '1', status: t.key === 'all' ? '' : t.key })}
          >
            {t.label}
          </Button>
        ))}
      </div>

      {!data || data.items.length === 0 ? (
        <EmptyState title="No applications" description="Apply to jobs from the job detail page to track them here." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="space-y-3 lg:col-span-2">
            {data.items.map((app) => (
              <Card key={app.id} className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Link to={`/jobs/${app.job_id}`} className="font-semibold hover:text-brand-600">{app.job_title}</Link>
                    <p className="text-sm text-slate-500">{app.company_name}</p>
                    <p className="text-xs text-slate-400">Updated {formatDate(app.updated_at)}</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setSelectedId(app.id)}>Details</Button>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={statusVariant[app.status]}>{app.status.replaceAll('_', ' ')}</Badge>
                  <Badge variant={app.priority >= 4 ? 'danger' : app.priority === 3 ? 'warning' : 'default'}>Priority {app.priority}</Badge>
                  <button
                    onClick={() => favoriteMutation.mutate({ id: app.id, is_favorite: !app.is_favorite })}
                    className="inline-flex items-center"
                  >
                    <Star className={`h-4 w-4 ${app.is_favorite ? 'fill-amber-400 text-amber-500' : 'text-slate-400'}`} />
                  </button>
                </div>
                <div className="text-xs text-slate-500">
                  Resume: {app.selected_resume_id ?? '—'} · Tailored: {app.selected_tailored_resume_id ?? '—'} · Cover Letter: {app.selected_cover_letter_id ?? '—'}
                </div>
                <div className="text-xs text-slate-500">
                  Interview Prepared: {app.interview_prepared ? 'Yes' : 'No'}
                  · Interview Completed: {app.interview_completed ? 'Yes' : 'No'}
                  · Readiness: {app.interview_readiness_score != null ? `${Math.round(app.interview_readiness_score)}%` : '—'}
                  · Practice Sessions: {app.interview_practice_sessions ?? 0}
                </div>
                {app.interview_preparation_id && (
                  <div className="flex flex-wrap gap-2">
                    <Link to={`/interview-prep/${app.interview_preparation_id}`}>
                      <Button size="sm" variant="outline">View Preparation</Button>
                    </Link>
                    {app.interview_completed && (
                      <Link to={`/interview-prep/${app.interview_preparation_id}/feedback`}>
                        <Button size="sm" variant="ghost">View Feedback</Button>
                      </Link>
                    )}
                  </div>
                )}
              </Card>
            ))}
            <Pagination
              page={data.page}
              size={data.size}
              total={data.total}
              onPageChange={(next) => setSearchParams({ page: String(next), status, favorites_only: String(favoritesOnly) })}
            />
          </div>

          <Card>
            {!selected ? (
              <p className="text-sm text-slate-500">Select an application to view and edit details.</p>
            ) : (
              <div className="space-y-3">
                <h3 className="font-semibold">{selected.job_title}</h3>
                <Select
                  value={selected.status}
                  onChange={(event) => updateMutation.mutate({ status: event.target.value as ApplicationStatus })}
                  options={tabs.filter((t) => t.key !== 'all').map((t) => ({ value: t.key, label: t.label }))}
                />
                <Select
                  value={String(selected.priority)}
                  onChange={(event) => updateMutation.mutate({ priority: Number(event.target.value) })}
                  options={[
                    { value: '1', label: 'Priority 1 (Low)' },
                    { value: '2', label: 'Priority 2' },
                    { value: '3', label: 'Priority 3' },
                    { value: '4', label: 'Priority 4' },
                    { value: '5', label: 'Priority 5 (Urgent)' },
                  ]}
                />
                <Textarea
                  label="Notes"
                  defaultValue={selected.notes ?? ''}
                  onBlur={(event) => updateMutation.mutate({ notes: event.target.value })}
                />
                <Button variant="outline" className="w-full" onClick={() => deleteMutation.mutate(selected.id)}>
                  Delete application
                </Button>
                <div className="rounded-lg border border-slate-200 p-3 text-xs dark:border-slate-700">
                  <p className="font-medium">Timeline</p>
                  <div className="mt-2 space-y-2">
                    {(history?.items ?? []).map((item) => (
                      <div key={item.id}>
                        <p>{item.from_status ?? 'new'} ΓåÆ {item.to_status}</p>
                        <p className="text-slate-400">{formatDateTime(item.created_at)}</p>
                      </div>
                    ))}
                    {(history?.items ?? []).length === 0 && <p className="text-slate-500">No history yet.</p>}
                  </div>
                </div>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
