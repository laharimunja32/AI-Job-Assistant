import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Card } from '@/components/ui';

interface OverallScoreRadarChartProps {
  atsScore: number;
  keywordMatch: number;
  skillMatch: number;
  experienceMatch: number;
  educationMatch: number;
}

export function OverallScoreRadarChart({
  atsScore,
  keywordMatch,
  skillMatch,
  experienceMatch,
  educationMatch,
}: OverallScoreRadarChartProps) {
  const data = [
    { metric: 'ATS', score: atsScore },
    { metric: 'Keywords', score: keywordMatch },
    { metric: 'Skills', score: skillMatch },
    { metric: 'Experience', score: experienceMatch },
    { metric: 'Education', score: educationMatch },
  ];

  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Overall Compatibility</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
            <Radar dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.35} />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
