import { Card } from '@/components/ui';

interface RecommendationPanelProps {
  recommendations: string[];
}

export function RecommendationPanel({ recommendations }: RecommendationPanelProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Recommendations</h3>
      {recommendations.length > 0 ? (
        <ul className="list-disc space-y-2 pl-5 text-sm text-slate-700 dark:text-slate-300">
          {recommendations.map((tip, index) => (
            <li key={`${tip}-${index}`}>{tip}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500">Run an analysis to receive tailored improvement suggestions.</p>
      )}
    </Card>
  );
}
