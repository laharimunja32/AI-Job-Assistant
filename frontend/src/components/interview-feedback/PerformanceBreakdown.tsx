import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui';
import type { PerformanceBreakdown as PerformanceBreakdownData } from '@/types';

interface PerformanceBreakdownProps {
  title?: string;
  breakdown: PerformanceBreakdownData;
}

export function PerformanceBreakdown({ title = 'Performance Breakdown', breakdown }: PerformanceBreakdownProps) {
  const data = Object.entries(breakdown).map(([skill, score]) => ({
    skill: skill.replace(/_/g, ' '),
    score,
  }));

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      {data.length === 0 ? (
        <p className="text-sm text-slate-500">Complete more interviews to see performance breakdown.</p>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
