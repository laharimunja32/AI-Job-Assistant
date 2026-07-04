import { X } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { LiveJobResult } from '@/services/jobSearch.service';

interface JobDetailsDrawerProps {
  job: LiveJobResult | null;
  open: boolean;
  onClose: () => void;
  onSave?: (job: LiveJobResult) => void;
  onStartApplication?: (job: LiveJobResult) => void;
}

export function JobDetailsDrawer({ job, open, onClose, onSave, onStartApplication }: JobDetailsDrawerProps) {
  if (!open || !job) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40">
      <div className="h-full w-full max-w-lg overflow-y-auto bg-white p-6 shadow-xl dark:bg-slate-900">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">{job.title}</h2>
            <p className="text-slate-500">{job.company}</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg p-2 hover:bg-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="mb-4 flex flex-wrap gap-2">
          {job.work_mode && <Badge variant="outline">{job.work_mode}</Badge>}
          {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
          {job.experience && <Badge variant="info">{job.experience}</Badge>}
        </div>
        {job.salary && <p className="mb-2 font-medium text-emerald-600">{job.salary}</p>}
        {job.location && <p className="mb-4 text-sm text-slate-500">{job.location}</p>}
        {job.description_preview && (
          <p className="mb-4 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{job.description_preview}</p>
        )}
        {job.skills.length > 0 && (
          <div className="mb-6 flex flex-wrap gap-1">
            {job.skills.map((s) => (
              <Badge key={s} variant="info">
                {s}
              </Badge>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <Button onClick={() => onSave?.(job)}>Save Job</Button>
          <Button variant="outline" onClick={() => onStartApplication?.(job)}>
            Start Application
          </Button>
        </div>
      </div>
    </div>
  );
}
