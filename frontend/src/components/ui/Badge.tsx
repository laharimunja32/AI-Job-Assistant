import { cn } from '@/utils';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'outline';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variants: Record<BadgeVariant, string> = {
  default: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  success: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  warning: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  danger: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  outline: 'border border-slate-300 bg-transparent text-slate-600 dark:border-slate-600 dark:text-slate-400',
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}

export function MatchScoreBadge({ score, category }: { score?: number | null; category?: string | null }) {
  if (score == null) return null;
  const variant =
    score >= 90 ? 'success' : score >= 75 ? 'info' : score >= 60 ? 'warning' : 'default';
  return (
    <Badge variant={variant}>
      {score}% {category ? `┬╖ ${category}` : ''}
    </Badge>
  );
}
