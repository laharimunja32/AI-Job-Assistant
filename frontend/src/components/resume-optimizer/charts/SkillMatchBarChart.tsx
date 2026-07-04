import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card } from '@/components/ui';

interface SkillMatchBarChartProps {
  matchedSkills: string[];
  missingSkills: string[];
}

export function SkillMatchBarChart({ matchedSkills, missingSkills }: SkillMatchBarChartProps) {
  const data = [
    { category: 'Matched', count: matchedSkills.length },
    { category: 'Missing', count: missingSkills.length },
  ];

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Skill Match</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
