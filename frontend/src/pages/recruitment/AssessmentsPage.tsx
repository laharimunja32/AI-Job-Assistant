import { useMemo, useState } from 'react';
import { useAssessments, useCreateAssessment, useUpdateAssessment } from '@/hooks';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input, Select } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { formatDateTime } from '@/utils';

const statuses = ['Pending', 'Scheduled', 'Completed', 'Expired', 'Cancelled'];

export default function AssessmentsPage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [view, setView] = useState<'list' | 'calendar'>('list');
  const { data } = useAssessments(page, 10, status || undefined);
  const createMutation = useCreateAssessment();
  const [draftType, setDraftType] = useState('');

  const filtered = useMemo(
    () =>
      (data?.items ?? []).filter((item) =>
        `${item.provider ?? ''} ${item.assessment_type ?? ''}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [data?.items, search],
  );

  const groupedByDay = useMemo(() => {
    const groups: Record<string, typeof filtered> = {};
    filtered.forEach((item) => {
      const key = item.deadline ? new Date(item.deadline).toDateString() : 'No deadline';
      groups[key] = [...(groups[key] ?? []), item];
    });
    return groups;
  }, [filtered]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Assessments</h1>
          <p className="mt-1 text-sm text-slate-500">Track provider tests, deadlines, status, and notes.</p>
        </div>
        <div className="flex gap-2">
          <Button variant={view === 'list' ? 'primary' : 'outline'} onClick={() => setView('list')}>List</Button>
          <Button variant={view === 'calendar' ? 'primary' : 'outline'} onClick={() => setView('calendar')}>Calendar View</Button>
        </div>
      </div>

      <Card className="flex gap-2">
        <Input placeholder="Quick add assessment type" value={draftType} onChange={(e) => setDraftType(e.target.value)} />
        <Button
          onClick={() => createMutation.mutate({ assessment_type: draftType || 'Online Assessment', status: 'Pending' })}
          disabled={!draftType}
        >
          Add
        </Button>
      </Card>

      <div className="grid gap-3 md:grid-cols-2">
        <Input placeholder="Search provider/type" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          options={[{ value: '', label: 'All statuses' }, ...statuses.map((s) => ({ value: s, label: s }))]}
        />
      </div>

      {view === 'list' ? (
        <div className="space-y-3">
          {filtered.map((item) => (
            <AssessmentRow key={item.id} id={item.id} title={item.assessment_type ?? 'Assessment'} provider={item.provider} deadline={item.deadline} status={item.status} />
          ))}
          {filtered.length === 0 && <Card><p className="text-sm text-slate-500">No assessments found.</p></Card>}
        </div>
      ) : (
        <div className="space-y-3">
          {Object.entries(groupedByDay).map(([day, items]) => (
            <Card key={day}>
              <p className="mb-2 font-semibold">{day}</p>
              <div className="space-y-2">
                {items.map((item) => (
                  <AssessmentRow key={item.id} id={item.id} title={item.assessment_type ?? 'Assessment'} provider={item.provider} deadline={item.deadline} status={item.status} />
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
      {data && <Pagination page={data.page} size={data.size} total={data.total} onPageChange={setPage} />}
    </div>
  );
}

function AssessmentRow({ id, title, provider, deadline, status }: { id: number; title: string; provider: string | null; deadline: string | null; status: string }) {
  const mutation = useUpdateAssessment(id);
  return (
    <Card className="flex items-center justify-between gap-3">
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-slate-500">{provider ?? 'Unknown provider'} · Deadline {deadline ? formatDateTime(deadline) : '—'}</p>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={status === 'Completed' ? 'success' : status === 'Expired' ? 'danger' : 'warning'}>{status}</Badge>
        <Button size="sm" variant="outline" onClick={() => mutation.mutate({ status: 'Completed' })}>Mark completed</Button>
      </div>
    </Card>
  );
}
