import { useState } from 'react';
import { useTimeline } from '@/hooks';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { formatDateTime } from '@/utils';

export default function TimelinePage() {
  const [applicationId, setApplicationId] = useState('1');
  const parsedId = Number(applicationId);
  const { data } = useTimeline(parsedId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Timeline</h1>
        <p className="mt-1 text-sm text-slate-500">Unified events for assessments, interviews, offers, reminders, and status changes.</p>
      </div>

      <Card>
        <Input label="Application ID" value={applicationId} onChange={(e) => setApplicationId(e.target.value)} />
      </Card>

      <div className="space-y-3">
        {(data?.items ?? []).map((item) => (
          <Card key={item.id}>
            <p className="font-medium">{item.title}</p>
            <p className="text-sm text-slate-500">{item.event_type} · {formatDateTime(item.event_time)}</p>
            {item.description && <p className="mt-2 text-sm">{item.description}</p>}
          </Card>
        ))}
        {(data?.items ?? []).length === 0 && <Card><p className="text-sm text-slate-500">No timeline events found for this application.</p></Card>}
      </div>
    </div>
  );
}
