import { Building2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';

interface CompanyCardProps {
  name: string;
  logo?: string | null;
  jobCount?: number;
  location?: string | null;
}

export function CompanyCard({ name, logo, jobCount, location }: CompanyCardProps) {
  return (
    <Card className="flex items-center gap-3">
      {logo ? (
        <img src={logo} alt="" className="h-12 w-12 rounded-lg object-cover" />
      ) : (
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
          <Building2 className="h-6 w-6" />
        </div>
      )}
      <div>
        <h3 className="font-semibold text-slate-900 dark:text-slate-100">{name}</h3>
        {location && <p className="text-sm text-slate-500">{location}</p>}
        {jobCount != null && <p className="text-xs text-slate-400">{jobCount} open roles</p>}
      </div>
    </Card>
  );
}
