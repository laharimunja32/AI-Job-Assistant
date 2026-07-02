import { Card } from '@/components/ui';

interface InterviewScoreCardProps {
  label: string;
  score: number | null | undefined;
  description?: string;
}

export function InterviewScoreCard({ label, score, description }: InterviewScoreCardProps) {
  return (
    <Card className="p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-slate-900 dark:text-slate-100">
        {score != null ? `${score}%` : '—'}
      </p>
      {description && <p className="mt-2 text-xs text-slate-500">{description}</p>}
    </Card>
  );
}
