import { Link } from 'react-router-dom';
import { AlertTriangle, Bell, Briefcase, Users } from 'lucide-react';
import { useNotificationCandidates, useNotificationHistory } from '@/hooks';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { parseApiError, formatDate } from '@/utils';

export default function NotificationsPage() {
  const { data, isLoading, error, refetch } = useNotificationCandidates();
  const { data: historyData } = useNotificationHistory(1, 20);

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  if (!data) return null;

  const totalUnread =
    data.newly_matched_jobs.length +
    data.newly_added_walk_ins.length +
    data.jobs_closing_soon.length +
    data.high_priority_opportunities.length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Notifications</h1>
        <p className="mt-1 text-sm text-slate-500">
          {totalUnread} notification{totalUnread !== 1 ? 's' : ''} from backend notification prep service
        </p>
      </div>

      <Card>
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-brand-50 p-2 dark:bg-brand-900/30">
            <Bell className="h-5 w-5 text-brand-600" />
          </div>
          <div>
            <p className="font-semibold">Notification Summary</p>
            <p className="text-sm text-slate-500">Delivery will be enabled in a future milestone</p>
          </div>
          {totalUnread > 0 && <Badge variant="danger" className="ml-auto">{totalUnread} unread</Badge>}
        </div>
      </Card>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Notification History</h2>
        <div className="space-y-2">
          {(historyData?.items ?? []).map((n) => (
            <Card key={n.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{n.title}</p>
                  <p className="text-sm text-slate-500">{n.message}</p>
                </div>
                <Badge variant={n.is_read ? 'default' : 'info'}>{n.notification_type}</Badge>
              </div>
            </Card>
          ))}
          {(historyData?.items ?? []).length === 0 && <Card><p className="text-sm text-slate-500">No notification history yet.</p></Card>}
        </div>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <AlertTriangle className="h-5 w-5 text-amber-500" /> High Priority
        </h2>
        <div className="space-y-2">
          {data.high_priority_opportunities.length === 0 ? (
            <Card><p className="text-sm text-slate-500">No high priority alerts.</p></Card>
          ) : (
            data.high_priority_opportunities.map((j, i) => (
              <Card key={i} className="flex items-center justify-between">
                <div>
                  {j.job_id ? (
                    <Link to={`/jobs/${j.job_id}`} className="font-medium hover:text-brand-600">{j.title}</Link>
                  ) : (
                    <p className="font-medium">{j.title}</p>
                  )}
                  <p className="text-sm text-slate-500">{j.company}</p>
                </div>
                {j.score != null && <Badge variant="success">{j.score}% match</Badge>}
              </Card>
            ))
          )}
        </div>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <Briefcase className="h-5 w-5 text-brand-500" /> Newly Matched Jobs
        </h2>
        <div className="space-y-2">
          {data.newly_matched_jobs.map((j, i) => (
            <Card key={i} className="flex items-center justify-between">
              <div>
                {j.job_id ? (
                  <Link to={`/jobs/${j.job_id}`} className="font-medium hover:text-brand-600">{j.title}</Link>
                ) : (
                  <p className="font-medium">{j.title}</p>
                )}
                <p className="text-sm text-slate-500">{j.company} ┬╖ {formatDate(j.matched_at)}</p>
              </div>
              {j.score != null && <Badge variant="info">{j.score}%</Badge>}
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <Users className="h-5 w-5 text-emerald-500" /> Walk-in Alerts
        </h2>
        <div className="space-y-2">
          {data.newly_added_walk_ins.map((w, i) => (
            <Card key={i}>
              {w.walk_in_id ? (
                <Link to={`/walk-ins/${w.walk_in_id}`} className="font-medium hover:text-brand-600">
                  {w.job_role} at {w.company_name}
                </Link>
              ) : (
                <p className="font-medium">{w.job_role} at {w.company_name}</p>
              )}
              <p className="text-sm text-slate-500">{w.city} ┬╖ {formatDate(w.walk_in_date)} ┬╖ {w.event_status}</p>
            </Card>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
          <AlertTriangle className="h-5 w-5 text-red-500" /> Closing Soon
        </h2>
        <div className="space-y-2">
          {data.jobs_closing_soon.map((j, i) => (
            <Card key={i} className="flex items-center justify-between">
              <div>
                {j.id ? (
                  <Link to={`/jobs/${j.id}`} className="font-medium hover:text-brand-600">{j.title}</Link>
                ) : (
                  <p className="font-medium">{j.title}</p>
                )}
                <p className="text-sm text-slate-500">{j.company} ┬╖ Deadline {formatDate(j.deadline)}</p>
              </div>
              <Badge variant="warning">{j.type}</Badge>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
