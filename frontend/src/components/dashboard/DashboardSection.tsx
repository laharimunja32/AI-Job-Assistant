import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface DashboardSectionProps {
  title: string;
  viewAllHref?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}

export function DashboardSection({ title, viewAllHref, children, action }: DashboardSectionProps) {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
        <div className="flex items-center gap-2">
          {action}
          {viewAllHref && (
            <Link to={viewAllHref}>
              <Button variant="ghost" size="sm">
                View all
              </Button>
            </Link>
          )}
        </div>
      </div>
      {children}
    </section>
  );
}

export function DashboardSectionCard({
  title,
  children,
  viewAllHref,
}: {
  title: string;
  children: React.ReactNode;
  viewAllHref?: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {viewAllHref && (
          <Link to={viewAllHref} className="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400">
            View all →
          </Link>
        )}
      </CardHeader>
      {children}
    </Card>
  );
}
