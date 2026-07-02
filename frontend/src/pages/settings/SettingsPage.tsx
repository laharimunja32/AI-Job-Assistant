import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { useUIStore } from '@/store';
import { useHealthCheck } from '@/hooks';
import { dashboardService } from '@/services';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Input';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError, formatDateTime } from '@/utils';
import type { Theme } from '@/types';

export default function SettingsPage() {
  const { theme, setTheme } = useUIStore();
  const { isLoading: healthLoading, isError: healthError } = useHealthCheck();
  const { addToast } = useToast();
  const [schedulerEnabled, setSchedulerEnabled] = useState(true);
  const [emailNotifs, setEmailNotifs] = useState(true);

  const { data: aggHistory } = useQuery({
    queryKey: ['aggregation-history'],
    queryFn: async () => {
      const { data } = await dashboardService.getAggregationHistory({ page: 1, size: 5 });
      return data;
    },
  });

  const handleTriggerAggregation = async () => {
    try {
      await dashboardService.triggerAggregation();
      addToast('Aggregation triggered', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">Manage your preferences and system status</p>
      </div>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Appearance</h2>
        <Select
          label="Theme"
          value={theme}
          onChange={(e) => setTheme(e.target.value as Theme)}
          options={[
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
            { value: 'system', label: 'System' },
          ]}
        />
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Password</h2>
        <p className="text-sm text-slate-500">
          Password change endpoint is not yet available. This section is prepared for a future backend module.
        </p>
        <Button className="mt-4" variant="outline" disabled>
          Change password
        </Button>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Notification Preferences</h2>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={emailNotifs} onChange={(e) => setEmailNotifs(e.target.checked)} className="rounded" />
          Email notifications (UI only — delivery coming soon)
        </label>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Scheduler Preferences</h2>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={schedulerEnabled} onChange={(e) => setSchedulerEnabled(e.target.checked)} className="rounded" />
          Enable background job refresh reminders (UI preference)
        </label>
        <Button className="mt-4" variant="outline" onClick={handleTriggerAggregation}>
          Trigger manual aggregation
        </Button>
        {aggHistory && aggHistory.items.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-sm font-medium">Recent aggregation runs</p>
            {aggHistory.items.map((run) => (
              <div key={run.id} className="rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
                <div className="flex justify-between">
                  <span>{run.run_type}</span>
                  <span className={run.status === 'completed' ? 'text-emerald-600' : 'text-amber-600'}>{run.status}</span>
                </div>
                <p className="text-xs text-slate-500">{formatDateTime(run.started_at)} · {run.jobs_created} created, {run.jobs_updated} updated</p>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">API Connection Status</h2>
        <div className="flex items-center gap-3">
          {healthLoading ? (
            <Loader2 className="h-5 w-5 animate-spin text-slate-400" />
          ) : healthError ? (
            <XCircle className="h-5 w-5 text-red-500" />
          ) : (
            <CheckCircle className="h-5 w-5 text-emerald-500" />
          )}
          <div>
            <p className="font-medium">
              {healthLoading ? 'Checking...' : healthError ? 'Disconnected' : 'Connected'}
            </p>
            <p className="text-sm text-slate-500">Backend API at /api/v1</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
