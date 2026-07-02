import { useState } from 'react';
import { useCreateReminder, useDeleteReminder, useReminders, useUpdateReminder } from '@/hooks';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { formatDateTime } from '@/utils';

export default function RemindersPage() {
  const [page, setPage] = useState(1);
  const [title, setTitle] = useState('');
  const [dueAt, setDueAt] = useState('');
  const { data } = useReminders(page, 10);
  const createMutation = useCreateReminder();
  const deleteMutation = useDeleteReminder();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reminders</h1>
        <p className="mt-1 text-sm text-slate-500">Set due reminders for assessments, interviews, and follow-ups.</p>
      </div>
      <Card className="grid gap-3 md:grid-cols-3">
        <Input placeholder="Reminder title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <Input type="datetime-local" value={dueAt} onChange={(e) => setDueAt(e.target.value)} />
        <Button
          onClick={() => createMutation.mutate({ title, due_at: new Date(dueAt).toISOString() })}
          disabled={!title || !dueAt}
        >
          Add Reminder
        </Button>
      </Card>

      <div className="space-y-3">
        {(data?.items ?? []).map((item) => (
          <ReminderRow key={item.id} id={item.id} title={item.title} due_at={item.due_at} status={item.status} onDelete={() => deleteMutation.mutate(item.id)} />
        ))}
        {(data?.items ?? []).length === 0 && <Card><p className="text-sm text-slate-500">No reminders yet.</p></Card>}
      </div>
      {data && <Pagination page={data.page} size={data.size} total={data.total} onPageChange={setPage} />}
    </div>
  );
}

function ReminderRow({ id, title, due_at, status, onDelete }: { id: number; title: string; due_at: string; status: string; onDelete: () => void }) {
  const mutation = useUpdateReminder(id);
  const overdue = new Date(due_at) < new Date() && !['completed', 'cancelled'].includes(status.toLowerCase());
  return (
    <Card className="flex items-center justify-between gap-2">
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm text-slate-500">Due {formatDateTime(due_at)}</p>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={overdue ? 'danger' : status === 'completed' ? 'success' : 'warning'}>{status}</Badge>
        <Button size="sm" variant="outline" onClick={() => mutation.mutate({ is_completed: true })}>Done</Button>
        <Button size="sm" variant="outline" onClick={onDelete}>Delete</Button>
      </div>
    </Card>
  );
}
