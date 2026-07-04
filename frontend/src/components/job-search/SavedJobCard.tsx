import { memo } from 'react';
import { Building2, MapPin, Trash2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { SavedJob } from '@/services/savedJobs.service';

interface SavedJobCardProps {
  job: SavedJob;
  onRemove?: (id: number) => void;
  onApply?: (job: SavedJob) => void;
}

export const SavedJobCard = memo(function SavedJobCard({ job, onRemove, onApply }: SavedJobCardProps) {
  return (
    <Card>
      <div className="flex items-start gap-3">
        {job.company_logo ? (
          <img src={job.company_logo} alt="" className="h-10 w-10 rounded-lg" />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
            <Building2 className="h-5 w-5" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">{job.job_title}</h3>
          <p className="text-sm text-slate-500">{job.company_name}</p>
          {job.location && (
            <p className="mt-1 inline-flex items-center gap-1 text-sm text-slate-500">
              <MapPin className="h-3.5 w-3.5" />
              {job.location}
            </p>
          )}
          {job.skills.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {job.skills.slice(0, 3).map((s) => (
                <Badge key={s} variant="info">
                  {s}
                </Badge>
              ))}
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button size="sm" onClick={() => onApply?.(job)}>
            Apply
          </Button>
          <Button size="sm" variant="outline" onClick={() => onRemove?.(job.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
});
