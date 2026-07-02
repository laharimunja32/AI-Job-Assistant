import { useMemo, useState } from 'react';
import {
  useApplications,
  useBrowserSessions,
  useBrowserReview,
  useConfirmBrowserReview,
  useDetectFormFields,
  useFillFormFields,
  useReviewHistory,
  useUploadAllDocuments,
  useValidateBrowserReview,
} from '@/hooks';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { parseApiError } from '@/utils';
import { useToast } from '@/contexts/ToastContext';

export default function ReviewAssistantPage() {
  const { addToast } = useToast();
  const sessionsQuery = useBrowserSessions();
  const applicationsQuery = useApplications({ page: 1, size: 50 });
  const detectForm = useDetectFormFields();
  const fillForm = useFillFormFields();
  const uploadAll = useUploadAllDocuments();
  const validateReview = useValidateBrowserReview();
  const confirmReview = useConfirmBrowserReview();

  const [sessionId, setSessionId] = useState('');
  const [applicationId, setApplicationId] = useState<number | undefined>(undefined);
  const [overrides, setOverrides] = useState<Record<string, string>>({});
  const reviewQuery = useBrowserReview(sessionId || undefined);
  const historyQuery = useReviewHistory(applicationId);
  const review = reviewQuery.data;
  const selectedApplication = useMemo(
    () => applicationsQuery.data?.items.find((item) => item.id === applicationId),
    [applicationsQuery.data?.items, applicationId],
  );

  const handleValidate = async () => {
    if (!sessionId) return;
    try {
      const response = await validateReview.mutateAsync(sessionId);
      addToast(response.data.valid ? 'Validation passed' : 'Validation has issues', response.data.valid ? 'success' : 'warning');
      reviewQuery.refetch();
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleConfirm = async (attemptSubmission: boolean) => {
    if (!sessionId) return;
    const ok = window.confirm(
      attemptSubmission
        ? 'Proceed with submission attempt? This only runs after explicit confirmation.'
        : 'Confirm review completion for this application?',
    );
    if (!ok) return;
    try {
      const response = await confirmReview.mutateAsync({
        sessionId,
        confirmed: true,
        attemptSubmission,
        reviewTimeSeconds: 60,
      });
      addToast(`Review result: ${response.data.result}`, 'success');
      reviewQuery.refetch();
      historyQuery.refetch();
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Guided Review</h1>
        <p className="mt-1 text-sm text-slate-500">
          Validate your application, review all detected data, and explicitly confirm before any submission attempt.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="mb-2 block text-sm font-medium">Browser Session</label>
            <select className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm" value={sessionId} onChange={(e) => setSessionId(e.target.value)}>
              <option value="">Select session</option>
              {(sessionsQuery.data?.items ?? []).map((session) => (
                <option key={session.session_id} value={session.session_id}>{session.session_id} ({session.browser_type})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Application</label>
            <select className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm" value={applicationId ?? ''} onChange={(e) => setApplicationId(e.target.value ? Number(e.target.value) : undefined)}>
              <option value="">Select application</option>
              {(applicationsQuery.data?.items ?? []).map((item) => (
                <option key={item.id} value={item.id}>#{item.id} {item.company_name} - {item.job_title}</option>
              ))}
            </select>
          </div>
          <div className="flex items-end gap-2">
            <Button disabled={!sessionId} loading={reviewQuery.isFetching} onClick={() => reviewQuery.refetch()}>Refresh Review</Button>
            <Button variant="outline" disabled={!sessionId} loading={validateReview.isPending} onClick={handleValidate}>Refresh Validation</Button>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-5">
        <Card><p className="text-xs text-slate-500">Readiness Score</p><p className="text-2xl font-bold">{review?.readiness.score ?? 0}%</p></Card>
        <Card><p className="text-xs text-slate-500">Filled Fields</p><p className="text-2xl font-bold">{review?.filled_fields.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Missing Required</p><p className="text-2xl font-bold">{review?.empty_required_fields.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Uploaded Docs</p><p className="text-2xl font-bold">{review?.uploaded_documents.length ?? 0}</p></Card>
        <Card><p className="text-xs text-slate-500">Warnings</p><p className="text-2xl font-bold">{review?.page_warnings.length ?? 0}</p></Card>
      </div>

      <Card>
        <h2 className="mb-3 text-lg font-semibold">Application Summary</h2>
        <div className="grid gap-3 text-sm md:grid-cols-3">
          <div><p className="text-slate-500">Job Details</p><p className="font-medium">{selectedApplication?.company_name ?? 'ΓÇö'} / {selectedApplication?.job_title ?? 'ΓÇö'}</p></div>
          <div><p className="text-slate-500">Selected Resume</p><p className="font-medium">{selectedApplication?.selected_resume_id ?? 'ΓÇö'}</p></div>
          <div><p className="text-slate-500">Selected Tailored Resume</p><p className="font-medium">{selectedApplication?.selected_tailored_resume_id ?? 'ΓÇö'}</p></div>
          <div><p className="text-slate-500">Selected Cover Letter</p><p className="font-medium">{selectedApplication?.selected_cover_letter_id ?? 'ΓÇö'}</p></div>
          <div><p className="text-slate-500">Browser Status</p><p className="font-medium">{review?.readiness.label ?? 'ΓÇö'}</p></div>
          <div><p className="text-slate-500">Current URL</p><p className="truncate font-medium">{review?.current_url ?? 'ΓÇö'}</p></div>
        </div>
      </Card>

      <Card className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Detected and Filled Fields</h2>
          <Button
            variant="outline"
            disabled={!sessionId}
            loading={fillForm.isPending}
            onClick={() => fillForm.mutate({ sessionId, overrides, traverseSteps: false })}
          >
            Re-run Auto-fill
          </Button>
        </div>
        {(review?.filled_fields ?? []).map((item) => (
          <div key={item.key} className="grid gap-2 rounded-lg border border-slate-200 p-3 text-sm md:grid-cols-4">
            <div className="font-medium">{item.label}</div>
            <div className="text-slate-600">{item.value}</div>
            <input
              className="rounded border border-slate-300 px-2 py-1"
              value={overrides[item.key] ?? ''}
              placeholder="Edit value override"
              onChange={(e) => setOverrides((prev) => ({ ...prev, [item.key]: e.target.value }))}
            />
            <div>{item.detail ?? ''}</div>
          </div>
        ))}
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h3 className="mb-2 font-semibold">Missing Required Fields</h3>
          {(review?.empty_required_fields ?? []).map((item) => <p key={item.key} className="text-sm">{item.label}</p>)}
          {!review?.empty_required_fields.length && <p className="text-sm text-slate-500">No missing required fields.</p>}
        </Card>
        <Card>
          <h3 className="mb-2 font-semibold">Uploaded Documents</h3>
          {(review?.uploaded_documents ?? []).map((item) => <p key={item.key} className="text-sm">{item.label}: {item.value}</p>)}
          {!review?.uploaded_documents.length && <p className="text-sm text-slate-500">No uploaded documents detected yet.</p>}
          <Button
            className="mt-3"
            variant="outline"
            disabled={!sessionId || !applicationId}
            loading={uploadAll.isPending}
            onClick={() => uploadAll.mutate({ sessionId, applicationId: applicationId as number, useTailoredResume: true })}
          >
            Re-run Uploads
          </Button>
        </Card>
      </div>

      <Card>
        <h3 className="mb-2 font-semibold">Warnings and Validation Errors</h3>
        {(review?.page_warnings ?? []).map((warning, idx) => <p key={`w-${idx}`} className="text-sm text-amber-700">{warning}</p>)}
        {(review?.validation_errors ?? []).map((error, idx) => <p key={`e-${idx}`} className="text-sm text-red-700">{error}</p>)}
        {!review?.page_warnings.length && !review?.validation_errors.length && <p className="text-sm text-slate-500">No warnings or validation errors.</p>}
      </Card>

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Review Actions</h3>
          <Badge variant={review?.readiness.score && review.readiness.score >= 85 ? 'success' : 'warning'}>
            {review?.readiness.recommended_action ?? 'Run validation first'}
          </Badge>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button disabled={!sessionId} loading={detectForm.isPending} onClick={() => detectForm.mutate(sessionId)}>Refresh Form Detection</Button>
          <Button variant="outline" disabled={!sessionId} onClick={() => handleConfirm(false)} loading={confirmReview.isPending}>Confirm Review</Button>
          <Button disabled={!sessionId} onClick={() => handleConfirm(true)} loading={confirmReview.isPending}>Proceed to Submission</Button>
        </div>
      </Card>

      <Card>
        <h3 className="mb-2 font-semibold">Submission History</h3>
        {(historyQuery.data?.items ?? []).map((item) => (
          <div key={item.id} className="mb-2 rounded border border-slate-200 p-3 text-sm">
            <p className="font-medium">{item.result}</p>
            <p>Readiness: {item.readiness_score}% | Validation: {item.validation_passed ? 'passed' : 'failed'}</p>
          </div>
        ))}
        {!historyQuery.data?.items.length && <p className="text-sm text-slate-500">No guided review history yet.</p>}
      </Card>
    </div>
  );
}
