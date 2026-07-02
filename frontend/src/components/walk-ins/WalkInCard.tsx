import { memo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Calendar, Clock, MapPin, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { formatDate } from '@/utils';
import type { DashboardWalkInItem, WalkIn } from '@/types';

type WalkInCardData = Pick<
  WalkIn | DashboardWalkInItem,
  | 'id'
  | 'company_name'
  | 'job_role'
  | 'venue'
  | 'city'
  | 'walk_in_date'
  | 'walk_in_time'
  | 'eligibility'
  | 'event_status'
  | 'registration_url'
>;

interface WalkInCardProps {
  walkIn: WalkInCardData;
  showAiBadge?: boolean;
}

export const WalkInCard = memo(function WalkInCard({ walkIn, showAiBadge }: WalkInCardProps) {
  const isToday = walkIn.event_status === 'Today';

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="transition-shadow hover:shadow-md">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          {isToday && <Badge variant="danger">Today</Badge>}
          {walkIn.event_status && !isToday && <Badge variant="info">{walkIn.event_status}</Badge>}
          {showAiBadge && <Badge variant="success">AI Matched</Badge>}
        </div>
        <Link to={`/walk-ins/${walkIn.id}`}>
          <h3 className="text-base font-semibold text-slate-900 hover:text-brand-600 dark:text-slate-100">
            {walkIn.job_role}
          </h3>
        </Link>
        <p className="mt-1 flex items-center gap-1 text-sm text-slate-500">
          <Building2 className="h-3.5 w-3.5" />
          {walkIn.company_name}
        </p>
        <div className="mt-3 space-y-1.5 text-sm text-slate-600 dark:text-slate-400">
          {(walkIn.venue || walkIn.city) && (
            <p className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 shrink-0" />
              {[walkIn.venue, walkIn.city].filter(Boolean).join(', ')}
            </p>
          )}
          {walkIn.walk_in_date && (
            <p className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5 shrink-0" />
              {formatDate(walkIn.walk_in_date)}
            </p>
          )}
          {walkIn.walk_in_time && (
            <p className="flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 shrink-0" />
              {walkIn.walk_in_time}
            </p>
          )}
        </div>
        {walkIn.eligibility && (
          <p className="mt-3 line-clamp-2 text-xs text-slate-500">{walkIn.eligibility}</p>
        )}
        <div className="mt-4 flex gap-2">
          <Link to={`/walk-ins/${walkIn.id}`}>
            <Button size="sm" variant="outline">
              Details
            </Button>
          </Link>
          {walkIn.registration_url && (
            <a href={walkIn.registration_url} target="_blank" rel="noopener noreferrer">
              <Button size="sm">
                Register <ExternalLink className="h-3.5 w-3.5" />
              </Button>
            </a>
          )}
        </div>
      </Card>
    </motion.div>
  );
});
