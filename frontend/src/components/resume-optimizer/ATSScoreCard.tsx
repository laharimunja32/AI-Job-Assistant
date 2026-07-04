import { Card } from '@/components/ui';
import { ATSGauge } from './charts/ATSGauge';

interface ATSScoreCardProps {
  atsScore: number;
  overallScore: number;
  keywordMatch: number;
  skillMatch: number;
  experienceMatch: number;
  educationMatch: number;
}

export function ATSScoreCard({
  atsScore,
  overallScore,
  keywordMatch,
  skillMatch,
  experienceMatch,
  educationMatch,
}: ATSScoreCardProps) {
  const rows = [
    { label: 'ATS Score', value: atsScore },
    { label: 'Keyword Match', value: keywordMatch },
    { label: 'Skills', value: skillMatch },
    { label: 'Experience', value: experienceMatch },
    { label: 'Education', value: educationMatch },
    { label: 'Overall', value: overallScore },
  ];

  return (
    <Card className="p-6">
      <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start sm:justify-between">
        <ATSGauge score={atsScore} size="lg" />
        <div className="w-full flex-1 space-y-2">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between text-sm">
              <span className="text-slate-500">{row.label}</span>
              <span className="font-semibold tabular-nums text-slate-900 dark:text-slate-100">{Math.round(row.value)}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
