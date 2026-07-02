import { useMemo, useState } from 'react';
import { useCreateInterview, useInterviews, useUpdateInterview } from '@/hooks';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input, Select } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { formatDateTime } from '@/utils';

const statuses = ['Scheduled', 'Completed', 'Cancelled', 'Rescheduled'];

export default function InterviewsPage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [draftType, setDraftType] = useState('Technical');
  const { data } = useInterviews(page, 10, status || undefined);
  const createMutation = useCreateInterview();

  const filtered = useMemo(
    () =>
      (data?.items ?? []).filter((item) =>
        `${item.interview_type} ${item.interviewer ?? ''}`.toLowerCase().includes(search.toLowerCase()),
      ),
    [data?.items, search],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Interviews</h1>
        <p className="mt-1 text-sm text-slate-500">Manage rounds, schedule details, links, and interviewer notes.</p>
      </div>
      <Card className="flex gap-2">
        <Input value={draftType} onChange={(e) => setDraftType(e.target.value)} placeholder="Interview type" />
        <Button onClick={() => createMutation.mutate({ interview_type: draftType, status: 'Scheduled' })}>Add</Button>
      </Card>
      <div className="grid gap-3 md:grid-cols-2">
        <Input placeholder="Search type/interviewer" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          options={[{ value: '', label: 'All statuses' }, ...statuses.map((s) => ({ value: s, label: s }))]}
        />
      </div>
      <div className="space-y-3">
        {filtered.map((item) => (
          <InterviewRow
            key={item.id}
            id={item.id}
            interview_type={item.interview_type}
            interviewer={item.interviewer}
            interview_date={item.interview_date}
            status={item.status}
          />
        ))}
        {filtered.length === 0 && <Card><p className="text-sm text-slate-500">No interviews found.</p></Card>}
      </div>
      {data && <Pagination page={data.page} size={data.size} total={data.total} onPageChange={setPage} />}
    </div>
  );
}

function InterviewRow(props: { id: number; interview_type: string; interviewer: string | null; interview_date: string | null; status: string }) {
  const mutation = useUpdateInterview(props.id);
  return (
    <Card className="flex items-center justify-between gap-3">
      <div>
        <p className="font-medium">{props.interview_type} Round</p>
        <p className="text-sm text-slate-500">{props.interviewer ?? 'TBD'} ┬╖ {props.interview_date ? formatDateTime(props.interview_date) : 'Not scheduled'}</p>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={props.status === 'Completed' ? 'success' : props.status === 'Cancelled' ? 'danger' : 'info'}>{props.status}</Badge>
        <Button size="sm" variant="outline" onClick={() => mutation.mutate({ status: 'Completed' })}>Complete</Button>
      </div>
    </Card>
  );
}
