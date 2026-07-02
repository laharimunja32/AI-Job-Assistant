import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui';
import type { SkillDistributionPoint } from '@/types';

interface SkillDistributionChartProps {
  distribution: SkillDistributionPoint[];
  title?: string;
}

export function SkillDistributionChart({
  distribution,
  title = 'Skill Distribution',
}: SkillDistributionChartProps) {
  const data = distribution.map((item) => ({
    skill: item.skill.replace(/_/g, ' '),
    score: item.score,
  }));

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      {data.length === 0 ? (
        <p className="text-sm text-slate-500">No skill distribution data yet.</p>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="skill" width={110} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="score" fill="#10b981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
