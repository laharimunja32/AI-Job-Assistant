import { formatDate } from '@/utils';
import { Badge } from '@/components/ui/Badge';
import type { BrowserApplication } from '@/services/browserApplication.service';

interface ApplicationHistoryTableProps {
  items: BrowserApplication[];
  onSelect?: (item: BrowserApplication) => void;
}

export function ApplicationHistoryTable({ items, onSelect }: ApplicationHistoryTableProps) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No application history yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
      <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
        <thead className="bg-slate-50 dark:bg-slate-900">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-slate-600">Company</th>
            <th className="px-4 py-3 text-left font-medium text-slate-600">Job</th>
            <th className="px-4 py-3 text-left font-medium text-slate-600">Status</th>
            <th className="px-4 py-3 text-left font-medium text-slate-600">Applied</th>
            <th className="px-4 py-3 text-left font-medium text-slate-600">Duration</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white dark:divide-slate-800 dark:bg-slate-950">
          {items.map((item) => (
            <tr
              key={item.id}
              className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900"
              onClick={() => onSelect?.(item)}
            >
              <td className="px-4 py-3">{item.company_name}</td>
              <td className="px-4 py-3">{item.job_title}</td>
              <td className="px-4 py-3">
                <Badge variant={item.status === 'completed' ? 'success' : 'outline'}>
                  {item.status.replace(/_/g, ' ')}
                </Badge>
              </td>
              <td className="px-4 py-3">{item.applied_date ? formatDate(item.applied_date) : '—'}</td>
              <td className="px-4 py-3">{item.duration_seconds != null ? `${item.duration_seconds}s` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
