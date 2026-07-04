import { CoverLetterCard } from './CoverLetterCard';
import { EmptyState } from '@/components/ui';
import type { CoverLetterGeneratorHistoryItem } from '@/types';

interface HistoryTableProps {
  items: CoverLetterGeneratorHistoryItem[];
}

export function HistoryTable({ items }: HistoryTableProps) {
  if (items.length === 0) {
    return <EmptyState title="No cover letters yet" description="Generate your first cover letter to see it here." />;
  }

  return (
    <div className="grid gap-4">
      {items.map((item) => (
        <CoverLetterCard key={item.id} item={item} />
      ))}
    </div>
  );
}
