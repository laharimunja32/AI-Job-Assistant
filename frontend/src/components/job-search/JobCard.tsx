import { memo } from 'react';
import { motion } from 'framer-motion';
import { Building2, MapPin, Bookmark } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import type { LiveJobResult } from '@/services/jobSearch.service';

interface JobCardProps {
  job: LiveJobResult;
  saved?: boolean;
  onSelect?: (job: LiveJobResult) => void;
  onSave?: (job: LiveJobResult) => void;
}

export const JobCard = memo(function JobCard({ job, saved, onSelect, onSave }: JobCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <Card className="group transition-shadow hover:shadow-md">
        <div className="flex items-start gap-3">
          {job.company_logo ? (
            <img src={job.company_logo} alt="" className="h-10 w-10 rounded-lg object-cover" />
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
              <Building2 className="h-5 w-5" />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              {job.work_mode && <Badge variant="outline">{job.work_mode}</Badge>}
              {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
            </div>
            <button type="button" onClick={() => onSelect?.(job)} className="block text-left">
              <h3 className="truncate text-base font-semibold text-slate-900 group-hover:text-brand-600 dark:text-slate-100">
                {job.title}
              </h3>
            </button>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-slate-500">
              <span className="inline-flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5" />
                {job.company}
              </span>
              {job.location && (
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" />
                  {job.location}
                </span>
              )}
            </div>
            {job.salary && (
              <p className="mt-2 text-sm font-medium text-emerald-600 dark:text-emerald-400">{job.salary}</p>
            )}
            {job.description_preview && (
              <p className="mt-2 line-clamp-2 text-sm text-slate-500">{job.description_preview}</p>
            )}
            {job.skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {job.skills.slice(0, 4).map((skill) => (
                  <Badge key={skill} variant="info">
                    {skill}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={() => onSave?.(job)}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-brand-600"
            aria-label={saved ? 'Remove from saved' : 'Save job'}
          >
            <Bookmark className={`h-5 w-5 ${saved ? 'fill-brand-500 text-brand-500' : ''}`} />
          </button>
        </div>
        <div className="mt-4 flex gap-2">
          <Button size="sm" variant="outline" onClick={() => onSelect?.(job)}>
            View Details
          </Button>
          {job.job_url && (
            <a href={job.job_url} target="_blank" rel="noreferrer">
              <Button size="sm">Apply</Button>
            </a>
          )}
        </div>
      </Card>
    </motion.div>
  );
});
