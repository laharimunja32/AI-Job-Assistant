import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card } from '@/components/ui';

interface KeywordMatchPieChartProps {
  matched: number;
  missing: number;
}

const COLORS = ['#6366f1', '#e2e8f0'];

export function KeywordMatchPieChart({ matched, missing }: KeywordMatchPieChartProps) {
  const data = [
    { name: 'Matched', value: matched },
    { name: 'Missing', value: missing },
  ].filter((item) => item.value > 0);

  if (data.length === 0) {
    return (
      <Card className="p-4">
        <h3 className="mb-2 text-sm font-semibold text-slate-900 dark:text-slate-100">Keyword Match</h3>
        <p className="text-sm text-slate-500">No keywords to compare.</p>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Keyword Match</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2}>
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
