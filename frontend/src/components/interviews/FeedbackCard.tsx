import { Card } from '@/components/ui';

interface FeedbackCardProps {
  title: string;
  items: string[];
  variant?: 'strength' | 'weakness' | 'default';
}

export function FeedbackCard({ title, items, variant = 'default' }: FeedbackCardProps) {
  const accent =
    variant === 'strength'
      ? 'border-emerald-200 dark:border-emerald-900'
      : variant === 'weakness'
        ? 'border-amber-200 dark:border-amber-900'
        : 'border-slate-200 dark:border-slate-800';

  return (
    <Card className={`p-4 ${accent}`}>
      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-600 dark:text-slate-300">
        {items.length > 0 ? items.map((item) => <li key={item}>{item}</li>) : <li>No items yet.</li>}
      </ul>
    </Card>
  );
}
