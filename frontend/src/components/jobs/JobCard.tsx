import { memo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bookmark, Building2, MapPin } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MatchScoreBadge, Badge } from '@/components/ui/Badge';
import { useBookmarksStore } from '@/store';
import type { DashboardJobItem, Job } from '@/types';

type JobCardJob = Pick<
  Job | DashboardJobItem,
  'id' | 'title' | 'company' | 'location' | 'work_mode' | 'employment_type' | 'salary' | 'match_score' | 'match_category' | 'matched_skills'
>;

interface JobCardProps {
  job: JobCardJob;
  showMatch?: boolean;
  compact?: boolean;
}

export const JobCard = memo(function JobCard({ job, showMatch = true, compact }: JobCardProps) {
  const { isBookmarked, toggleBookmark } = useBookmarksStore();
  const bookmarked = isBookmarked(job.id);

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <Card className="group transition-shadow hover:shadow-md">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              {showMatch && <MatchScoreBadge score={job.match_score} category={job.match_category} />}
              {job.work_mode && <Badge variant="outline">{job.work_mode}</Badge>}
              {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
            </div>
            <Link to={`/jobs/${job.id}`} className="block">
              <h3 className="truncate text-base font-semibold text-slate-900 group-hover:text-brand-600 dark:text-slate-100 dark:group-hover:text-brand-400">
                {job.title}
              </h3>
            </Link>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
              <span className="inline-flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5" />
                {job.company ?? 'Unknown'}
              </span>
              {job.location && (
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5" />
                  {job.location}
                </span>
              )}
            </div>
            {!compact && job.salary && (
              <p className="mt-2 text-sm font-medium text-emerald-600 dark:text-emerald-400">{job.salary}</p>
            )}
            {!compact && job.matched_skills && job.matched_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {job.matched_skills.slice(0, 4).map((s) => (
                  <Badge key={s} variant="info">
                    {s}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={() =>
              toggleBookmark({ id: job.id, title: job.title, company: job.company ?? 'Unknown' })
            }
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-brand-600 dark:hover:bg-slate-800"
            aria-label={bookmarked ? 'Remove bookmark' : 'Bookmark job'}
          >
            <Bookmark className={`h-5 w-5 ${bookmarked ? 'fill-brand-500 text-brand-500' : ''}`} />
          </button>
        </div>
        {!compact && (
          <div className="mt-4 flex gap-2">
            <Link to={`/jobs/${job.id}`}>
              <Button size="sm" variant="outline">
                View Details
              </Button>
            </Link>
          </div>
        )}
      </Card>
    </motion.div>
  );
});

export function JobListGrid({ children }: { children: React.ReactNode }) {
  return <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{children}</div>;
}
