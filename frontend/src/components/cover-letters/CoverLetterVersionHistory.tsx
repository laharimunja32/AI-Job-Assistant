import type { CoverLetterGenerationHistoryItem } from '@/types';
import { Card } from '@/components/ui/Card';

export function CoverLetterVersionHistory({ items }: { items: CoverLetterGenerationHistoryItem[] }) {
  return (
    <Card>
      <p className="mb-2 text-sm font-medium">Version history</p>
      {items.length > 0 ? (
        <ul className="space-y-2 text-xs">
          {items.slice(0, 5).map((item) => (
            <li key={item.id} className="rounded-lg border border-slate-200 p-2 dark:border-slate-700">
              Job #{item.job_id} · {item.status} · retry {item.retry_count}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-slate-500">No previous versions.</p>
      )}
    </Card>
  );
}
