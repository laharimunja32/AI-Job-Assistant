import { useMemo, useState } from 'react';
import { useBrowserSessions, useDetectFormFields, useFillFormFields, useFormFillReport } from '@/hooks';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { parseApiError } from '@/utils';

export default function FormAssistantPage() {
  const sessionsQuery = useBrowserSessions();
  const detectMutation = useDetectFormFields();
  const fillMutation = useFillFormFields();
  const [sessionId, setSessionId] = useState<string>('');
  const [overrides, setOverrides] = useState<Record<string, string>>({});

  const reportQuery = useFormFillReport(sessionId || undefined);
  const detection = detectMutation.data?.data;
  const report = reportQuery.data ?? fillMutation.data?.data;

  const confidenceAverage = useMemo(() => {
    if (!detection?.fields.length) return 0;
    const total = detection.fields.reduce((sum, field) => sum + field.confidence, 0);
    return Math.round((total / detection.fields.length) * 100);
  }, [detection]);

  const error = useMemo(
    () => [detectMutation.error, fillMutation.error, reportQuery.error].find(Boolean),
    [detectMutation.error, fillMutation.error, reportQuery.error],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Form Assistant</h1>
        <p className="mt-1 text-sm text-slate-500">
          Detect fields and auto-fill supported values from your profile. CAPTCHAs and submission are intentionally disabled.
        </p>
      </div>

      <Card className="space-y-3">
        <label className="block text-sm font-medium">Browser Session</label>
        <div className="flex flex-wrap gap-2">
          <select
            className="min-w-[260px] rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
          >
            <option value="">Select active session</option>
            {sessionsQuery.data?.items.map((session) => (
              <option key={session.session_id} value={session.session_id}>
                {session.session_id} ({session.browser_type})
              </option>
            ))}
          </select>
          <Button disabled={!sessionId} loading={detectMutation.isPending} onClick={() => detectMutation.mutate(sessionId)}>
            Detect Fields
          </Button>
          <Button
            variant="outline"
            disabled={!sessionId}
            loading={fillMutation.isPending}
            onClick={() => fillMutation.mutate({ sessionId, overrides, traverseSteps: true })}
          >
            Auto Fill
          </Button>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><p className="text-xs text-slate-500">Detected Fields</p><p className="text-2xl font-bold">{detection?.total_fields ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Auto-filled Fields</p><p className="text-2xl font-bold">{report?.filled_fields.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Manual Fields</p><p className="text-2xl font-bold">{report?.required_manual_input.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Completion</p><p className="text-2xl font-bold">{Math.round(report?.completion_percentage ?? 0)}%</p></Card>
      </div>

      {error && (
        <Card className="border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40">
          <p className="text-sm text-red-700 dark:text-red-300">{parseApiError(error)}</p>
        </Card>
      )}

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Detected Fields</h2>
          <Badge variant="info">Avg Confidence {confidenceAverage}%</Badge>
        </div>
        {(detection?.fields ?? []).map((field) => (
          <div key={field.field_id} className="grid gap-2 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700 md:grid-cols-5">
            <div>
              <p className="font-medium">{field.field_type}</p>
              <p className="text-xs text-slate-500">{field.selector}</p>
            </div>
            <div className="text-slate-600 dark:text-slate-300">{field.label ?? field.placeholder ?? 'Unlabeled'}</div>
            <div className="text-slate-600 dark:text-slate-300">{field.required ? 'Required' : 'Optional'}</div>
            <div className="text-slate-600 dark:text-slate-300">{Math.round(field.confidence * 100)}%</div>
            <Input
              placeholder="Optional override value"
              value={overrides[field.field_id] ?? ''}
              onChange={(e) => setOverrides((prev) => ({ ...prev, [field.field_id]: e.target.value }))}
            />
          </div>
        ))}
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h3 className="mb-2 font-semibold">Missing Fields</h3>
          <div className="space-y-2 text-sm">
            {(report?.unknown_fields ?? []).map((field) => (
              <p key={field.field_id}>{field.field_type}</p>
            ))}
            {!(report?.unknown_fields.length) && <p className="text-slate-500">No missing mappings.</p>}
          </div>
        </Card>
        <Card>
          <h3 className="mb-2 font-semibold">Required Manual Input</h3>
          <div className="space-y-2 text-sm">
            {(report?.required_manual_input ?? []).map((field) => (
              <p key={field.field_id}>{field.field_type}</p>
            ))}
            {!(report?.required_manual_input.length) && <p className="text-slate-500">No manual input currently required.</p>}
          </div>
        </Card>
      </div>
    </div>
  );
}
