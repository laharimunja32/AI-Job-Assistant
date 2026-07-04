import { Link } from 'react-router-dom';
import { Badge, Card } from '@/components/ui';
import { formatDate } from '@/utils';
import type { CoverLetterGeneratorHistoryItem } from '@/types';

interface CoverLetterCardProps {
  item: CoverLetterGeneratorHistoryItem;
}

export function CoverLetterCard({ item }: CoverLetterCardProps) {
  return (
    <Link to={`/cover-letter-generator/${item.id}`}>
      <Card className="flex flex-wrap items-center justify-between gap-4 p-4 transition-colors hover:border-brand-300 dark:hover:border-brand-700">
        <div>
          <p className="font-medium text-slate-900 dark:text-slate-100">
            {item.job_title ?? 'Untitled Role'}
            {item.company_name ? ` at ${item.company_name}` : ''}
          </p>
          <p className="text-xs text-slate-500">
            Resume #{item.resume_id} · {formatDate(item.created_at)}
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant="default">{item.template_name}</Badge>
          <Badge variant="info">{item.tone}</Badge>
        </div>
      </Card>
    </Link>
  );
}
