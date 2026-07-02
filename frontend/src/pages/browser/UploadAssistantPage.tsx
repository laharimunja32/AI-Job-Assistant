import { useMemo, useState } from 'react';
import { useApplications, useBrowserSessions, useDetectUploadFields, useRetryUpload, useUploadAllDocuments, useUploadStatus } from '@/hooks';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { parseApiError } from '@/utils';

export default function UploadAssistantPage() {
  const sessionsQuery = useBrowserSessions();
  const applicationsQuery = useApplications({ page: 1, size: 50 });
  const detectMutation = useDetectUploadFields();
  const uploadMutation = useUploadAllDocuments();
  const retryMutation = useRetryUpload();

  const [sessionId, setSessionId] = useState('');
  const [applicationId, setApplicationId] = useState<number | undefined>(undefined);
  const [useTailoredResume, setUseTailoredResume] = useState(true);

  const statusQuery = useUploadStatus(sessionId || undefined, applicationId);
  const detection = detectMutation.data?.data;
  const uploadStatus = statusQuery.data ?? uploadMutation.data?.data ?? retryMutation.data?.data;
  const selectedApplication = useMemo(
    () => applicationsQuery.data?.items.find((item) => item.id === applicationId),
    [applicationsQuery.data?.items, applicationId],
  );

  const error = useMemo(
    () => [detectMutation.error, uploadMutation.error, retryMutation.error, statusQuery.error].find(Boolean),
    [detectMutation.error, uploadMutation.error, retryMutation.error, statusQuery.error],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Upload Assistant</h1>
        <p className="mt-1 text-sm text-slate-500">
          Intelligent resume and cover letter upload for active browser sessions. Final submission is intentionally disabled.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="mb-2 block text-sm font-medium">Browser Session</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
            >
              <option value="">Select session</option>
              {(sessionsQuery.data?.items ?? []).map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {session.session_id} ({session.browser_type})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Application</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
              value={applicationId ?? ''}
              onChange={(e) => setApplicationId(e.target.value ? Number(e.target.value) : undefined)}
            >
              <option value="">Select application</option>
              {(applicationsQuery.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>
                  #{item.id} {item.company_name} - {item.job_title}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end gap-2">
            <Button disabled={!sessionId} loading={detectMutation.isPending} onClick={() => detectMutation.mutate(sessionId)}>
              Detect Upload Fields
            </Button>
            <Button
              variant="outline"
              disabled={!sessionId || !applicationId}
              loading={uploadMutation.isPending}
              onClick={() =>
                uploadMutation.mutate({
                  sessionId,
                  applicationId: applicationId as number,
                  useTailoredResume,
                })
              }
            >
              Upload All
            </Button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input id="tailored" type="checkbox" checked={useTailoredResume} onChange={(e) => setUseTailoredResume(e.target.checked)} />
          <label htmlFor="tailored" className="text-sm">Prefer tailored resume when available</label>
        </div>
      </Card>

      {error && (
        <Card className="border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40">
          <p className="text-sm text-red-700 dark:text-red-300">{parseApiError(error)}</p>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card><p className="text-xs text-slate-500">Detected Upload Fields</p><p className="text-2xl font-bold">{detection?.total_fields ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Uploaded</p><p className="text-2xl font-bold">{uploadStatus?.uploaded_fields.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Failed</p><p className="text-2xl font-bold">{uploadStatus?.failed_fields.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Status</p><p className="text-sm font-semibold capitalize">{uploadStatus?.status ?? 'idle'}</p></Card>
      </div>

      <Card>
        <h2 className="mb-3 text-lg font-semibold">Selected Documents</h2>
        <div className="grid gap-3 md:grid-cols-3 text-sm">
          <div><p className="text-slate-500">Selected Resume</p><p className="font-medium">{selectedApplication?.selected_resume_id ?? '—'}</p></div>
          <div><p className="text-slate-500">Selected Tailored Resume</p><p className="font-medium">{selectedApplication?.selected_tailored_resume_id ?? '—'}</p></div>
          <div><p className="text-slate-500">Selected Cover Letter</p><p className="font-medium">{selectedApplication?.selected_cover_letter_id ?? '—'}</p></div>
        </div>
      </Card>

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Detected Upload Fields</h2>
          <Badge variant="info">Detection</Badge>
        </div>
        {(detection?.fields ?? []).map((field) => (
          <div key={field.field_id} className="grid gap-2 rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700 md:grid-cols-6">
            <div className="font-medium">{field.field_type}</div>
            <div className="text-slate-600 dark:text-slate-300">{field.selector}</div>
            <div>{Math.round(field.confidence * 100)}%</div>
            <div>{field.visible ? 'Visible' : 'Hidden'}</div>
            <div>{field.upload_capability}</div>
            <Input readOnly value={field.nearby_text ?? ''} />
          </div>
        ))}
      </Card>

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Upload History</h2>
          <Button
            variant="outline"
            disabled={!sessionId || !applicationId}
            loading={retryMutation.isPending}
            onClick={() => retryMutation.mutate({ sessionId, applicationId: applicationId as number, includeResume: true, includeCoverLetter: true })}
          >
            Retry
          </Button>
        </div>
        {[...(uploadStatus?.uploaded_fields ?? []), ...(uploadStatus?.failed_fields ?? []), ...(uploadStatus?.pending_fields ?? [])].map((item, idx) => (
          <div key={`${item.selector}-${idx}`} className="rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium capitalize">{item.field_type} - {item.status}</p>
              <Badge variant={item.status === 'uploaded' ? 'success' : item.status === 'failed' ? 'danger' : 'default'}>
                {item.filename ?? item.document_type ?? 'pending'}
              </Badge>
            </div>
            <p className="text-xs text-slate-500">{item.selector}</p>
            {item.error && <p className="mt-1 text-xs text-red-600 dark:text-red-300">{item.error}</p>}
          </div>
        ))}
        {!(uploadStatus?.uploaded_fields.length || uploadStatus?.failed_fields.length || uploadStatus?.pending_fields.length) && (
          <p className="text-sm text-slate-500">No upload history for this application yet.</p>
        )}
      </Card>
    </div>
  );
}
