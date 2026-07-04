import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useStartBrowserApplication, useSubmitBrowserApplication } from '@/hooks';
import { ApplicationProgress, AutomationStatus } from '@/components/job-search';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';
import type { BrowserApplication } from '@/services/browserApplication.service';

export default function BrowserApplicationPage() {
  const location = useLocation();
  const { addToast } = useToast();
  const startMutation = useStartBrowserApplication();
  const submitMutation = useSubmitBrowserApplication();
  const [record, setRecord] = useState<BrowserApplication | null>(null);
  const [form, setForm] = useState({
    job_title: '',
    company_name: '',
    apply_url: '',
    job_id: undefined as number | undefined,
  });

  useEffect(() => {
    const state = location.state as Record<string, unknown> | null;
    if (state) {
      setForm({
        job_title: String(state.job_title ?? ''),
        company_name: String(state.company_name ?? ''),
        apply_url: String(state.apply_url ?? ''),
        job_id: state.job_id ? Number(state.job_id) : undefined,
      });
    }
  }, [location.state]);

  const handleStart = async () => {
    try {
      const { data } = await startMutation.mutateAsync({
        job_id: form.job_id,
        job_title: form.job_title,
        company_name: form.company_name,
        apply_url: form.apply_url || undefined,
      });
      setRecord(data);
      addToast('Application automation started', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleSubmit = async () => {
    if (!record) return;
    try {
      const { data } = await submitMutation.mutateAsync({ id: record.id });
      setRecord(data);
      addToast('Application submitted', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const stepIndex = record
    ? Math.min(((record.metadata?.steps as string[]) ?? []).length, 5)
    : 0;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Browser Application</h1>
        <p className="mt-1 text-sm text-slate-500">Automate job applications with Playwright</p>
      </div>

      <Card className="space-y-4">
        <Input
          label="Job Title"
          value={form.job_title}
          onChange={(e) => setForm({ ...form, job_title: e.target.value })}
        />
        <Input
          label="Company"
          value={form.company_name}
          onChange={(e) => setForm({ ...form, company_name: e.target.value })}
        />
        <Input
          label="Apply URL"
          value={form.apply_url}
          onChange={(e) => setForm({ ...form, apply_url: e.target.value })}
        />
        <div className="flex gap-2">
          <Button onClick={handleStart} loading={startMutation.isPending} disabled={!form.job_title || !form.company_name}>
            Start Application
          </Button>
          {record && record.status !== 'completed' && (
            <Button variant="outline" onClick={handleSubmit} loading={submitMutation.isPending}>
              Submit Application
            </Button>
          )}
        </div>
      </Card>

      <ApplicationProgress currentStep={stepIndex} status={record?.status} />

      {record && <AutomationStatus application={record} />}
    </div>
  );
}
