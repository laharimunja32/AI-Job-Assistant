import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';
import type { BrowserApplication } from '@/services/browserApplication.service';

const statusVariant = (status: string) => {
  if (status === 'completed') return 'success' as const;
  if (status === 'failed') return 'danger' as const;
  if (status === 'manual_required') return 'warning' as const;
  return 'outline' as const;
};

interface AutomationStatusProps {
  application: BrowserApplication;
}

export function AutomationStatus({ application }: AutomationStatusProps) {
  const steps = (application.metadata?.steps as string[]) ?? [];
  return (
    <Card>
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">{application.job_title}</h3>
          <p className="text-sm text-slate-500">{application.company_name}</p>
        </div>
        <Badge variant={statusVariant(application.status)}>{application.status.replace(/_/g, ' ')}</Badge>
      </div>
      <div className="mt-4 grid gap-2 text-sm text-slate-600 md:grid-cols-2">
        <p>Session: {application.browser_session_id ?? '—'}</p>
        <p>Duration: {application.duration_seconds != null ? `${application.duration_seconds}s` : '—'}</p>
        <p>Steps: {steps.join(' → ') || '—'}</p>
        {application.error_message && <p className="text-red-600 md:col-span-2">{application.error_message}</p>}
      </div>
    </Card>
  );
}
