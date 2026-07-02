import { useMemo, useState } from 'react';
import {
  useBrowserSessions,
  useBrowserStatus,
  useCloseBrowserSession,
  useCreateBrowserSession,
  useOpenApplicationInBrowser,
  useRestartBrowserSession,
} from '@/hooks';
import type { BrowserType } from '@/types';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { parseApiError } from '@/utils';

const browserOptions: BrowserType[] = ['chromium', 'edge', 'firefox'];

export default function BrowserAutomationPage() {
  const [browserType, setBrowserType] = useState<BrowserType>('chromium');
  const [applicationId, setApplicationId] = useState('');
  const [selectedSessionId, setSelectedSessionId] = useState<string | undefined>(undefined);

  const sessionsQuery = useBrowserSessions();
  const statusQuery = useBrowserStatus();
  const createMutation = useCreateBrowserSession();
  const openMutation = useOpenApplicationInBrowser();
  const closeMutation = useCloseBrowserSession();
  const restartMutation = useRestartBrowserSession();

  const sessions = sessionsQuery.data?.items ?? [];
  const actionError = useMemo(
    () => [createMutation.error, openMutation.error, closeMutation.error, restartMutation.error].find(Boolean),
    [createMutation.error, openMutation.error, closeMutation.error, restartMutation.error],
  );

  const launchBrowser = async () => {
    const result = await createMutation.mutateAsync({ browser_type: browserType });
    setSelectedSessionId(result.data.session_id);
  };

  const openApplication = async () => {
    const parsedId = Number(applicationId);
    if (!parsedId) return;
    await openMutation.mutateAsync({
      applicationId: parsedId,
      sessionId: selectedSessionId,
      browserType,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Browser Automation</h1>
        <p className="mt-1 text-sm text-slate-500">
          Foundation layer for Playwright browser sessions and navigation. Use the Form Assistant page for detection and profile-based auto-fill.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="mb-2 block text-sm font-medium">Browser Type</label>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
              value={browserType}
              onChange={(e) => setBrowserType(e.target.value as BrowserType)}
            >
              {browserOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Application ID</label>
            <Input
              placeholder="e.g. 42"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
              type="number"
            />
          </div>
          <div className="flex items-end gap-2">
            <Button onClick={launchBrowser} loading={createMutation.isPending}>
              Launch Browser
            </Button>
            <Button variant="outline" onClick={openApplication} loading={openMutation.isPending}>
              Open Application
            </Button>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><p className="text-sm text-slate-500">Active Sessions</p><p className="text-2xl font-bold">{statusQuery.data?.active_sessions ?? 0}</p></Card>
        <Card><p className="text-sm text-slate-500">Browser Status</p><p className="text-2xl font-bold capitalize">{statusQuery.data?.browser_status ?? 'unknown'}</p></Card>
        <Card><p className="text-sm text-slate-500">Success Rate</p><p className="text-2xl font-bold">{Math.round(statusQuery.data?.navigation_success_rate ?? 0)}%</p></Card>
        <Card><p className="text-sm text-slate-500">Last Activity</p><p className="text-sm font-medium">{statusQuery.data?.last_browser_activity ?? '—'}</p></Card>
      </div>

      {actionError && (
        <Card className="border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40">
          <p className="text-sm text-red-700 dark:text-red-300">{parseApiError(actionError)}</p>
        </Card>
      )}

      <div className="space-y-3">
        {sessions.map((session) => (
          <Card key={session.session_id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="space-y-1 text-sm">
                <p><span className="font-semibold">Session:</span> {session.session_id}</p>
                <p><span className="font-semibold">Browser:</span> {session.browser_type}</p>
                <p><span className="font-semibold">Current URL:</span> {session.current_url ?? 'Not opened yet'}</p>
                <p><span className="font-semibold">Navigation Progress:</span> {session.metadata?.title ?? 'Pending'}</p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={session.status === 'failed' ? 'danger' : session.status === 'active' ? 'success' : 'default'}>
                  {session.status}
                </Badge>
                <Button variant="outline" onClick={() => setSelectedSessionId(session.session_id)}>Use Session</Button>
                <Button
                  variant="outline"
                  loading={restartMutation.isPending}
                  onClick={() => restartMutation.mutate({ sessionId: session.session_id })}
                >
                  Restart
                </Button>
                <Button
                  variant="ghost"
                  loading={closeMutation.isPending}
                  onClick={() => closeMutation.mutate(session.session_id)}
                >
                  Close
                </Button>
              </div>
            </div>
            {session.error_message && <p className="mt-3 text-sm text-red-600 dark:text-red-300">{session.error_message}</p>}
            {session.screenshot_path && (
              <div className="mt-3 text-xs text-slate-500">
                Screenshot: {session.screenshot_path}
              </div>
            )}
          </Card>
        ))}

        {!sessionsQuery.isLoading && sessions.length === 0 && (
          <Card>
            <p className="text-sm text-slate-500">No browser sessions yet.</p>
          </Card>
        )}
      </div>
    </div>
  );
}
