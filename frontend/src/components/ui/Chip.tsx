import { X } from 'lucide-react';
import { cn } from '@/utils';

interface ChipProps {
  label: string;
  onRemove?: () => void;
  className?: string;
}

export function Chip({ label, onRemove, className }: ChipProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700 dark:bg-brand-900/30 dark:text-brand-300',
        className,
      )}
    >
      {label}
      {onRemove && (
        <button onClick={onRemove} className="rounded-full p-0.5 hover:bg-brand-100 dark:hover:bg-brand-800" aria-label={`Remove ${label}`}>
          <X className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}
