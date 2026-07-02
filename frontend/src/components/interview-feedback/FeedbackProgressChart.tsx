import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui';
import type { ScoreTrendPoint } from '@/types';
import { formatDate } from '@/utils';

interface FeedbackProgressChartProps {
  trend: ScoreTrendPoint[];
  title?: string;
}

export function FeedbackProgressChart({ trend, title = 'Score Trend' }: FeedbackProgressChartProps) {
  const data = trend.map((point) => ({
    date: formatDate(point.date),
    score: point.overall_score ?? 0,
    feedbackId: point.feedback_id,
  }));

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      {data.length === 0 ? (
        <p className="text-sm text-slate-500">Complete interviews to track your score trend.</p>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#4f46e5" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
