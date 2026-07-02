import { Link } from 'react-router-dom';
import { Badge, Button, Card } from '@/components/ui';
import type { InterviewHistoryItem, InterviewPreparation } from '@/types';
import { ReadinessGauge } from './ReadinessGauge';

interface InterviewCardProps {
  preparation?: InterviewPreparation;
  historyItem?: InterviewHistoryItem;
  jobTitle?: string;
  companyName?: string;
}

export function InterviewCard({ preparation, historyItem, jobTitle, companyName }: InterviewCardProps) {
  const id = preparation?.id ?? historyItem?.preparation_id;
  const title = jobTitle ?? historyItem?.job_title ?? `Job #${preparation?.job_id ?? historyItem?.job_id}`;
  const company = companyName ?? historyItem?.company_name ?? 'Company';
  const score = preparation?.readiness_score ?? historyItem?.readiness_score ?? historyItem?.overall_score;

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</p>
          <p className="text-sm text-slate-500">{company}</p>
          {preparation && (
            <div className="mt-2 flex flex-wrap gap-2">
              <Badge variant={preparation.status === 'completed' ? 'success' : 'warning'}>{preparation.status}</Badge>
              {preparation.estimated_duration_minutes && (
                <Badge variant="default">~{preparation.estimated_duration_minutes} min</Badge>
              )}
            </div>
          )}
          {historyItem?.completed_at && (
            <p className="mt-2 text-xs text-slate-500">
              Completed {new Date(historyItem.completed_at).toLocaleString()}
            </p>
          )}
        </div>
        {score != null && <ReadinessGauge score={score} size="sm" />}
      </div>
      {id && (
        <div className="mt-4 flex gap-2">
          <Link to={`/interview-prep/${id}`}>
            <Button size="sm" variant="outline">View</Button>
          </Link>
          {preparation?.status === 'completed' && (
            <Link to={`/interview-prep/${id}/practice`}>
              <Button size="sm">Practice</Button>
            </Link>
          )}
          {historyItem && (
            <Link to={`/interview-prep/${id}/feedback`}>
              <Button size="sm" variant="ghost">Feedback</Button>
            </Link>
          )}
        </div>
      )}
    </Card>
  );
}
