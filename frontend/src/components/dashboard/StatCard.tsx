import { memo } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, TrendingUp, MapPin, Users, Target, ClipboardList, Star, XCircle } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import type { DashboardStatistics } from '@/types';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  href?: string;
  trend?: string;
}

export const StatCard = memo(function StatCard({ label, value, icon, href, trend }: StatCardProps) {
  const content = (
    <Card className="transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-slate-100">{value}</p>
          {trend && <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400">{trend}</p>}
        </div>
        <div className="rounded-lg bg-brand-50 p-2.5 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
          {icon}
        </div>
      </div>
    </Card>
  );

  return href ? <Link to={href}>{content}</Link> : content;
});

export function DashboardStats({ stats }: { stats: DashboardStatistics }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Active Jobs" value={stats.total_active_jobs} icon={<Briefcase className="h-5 w-5" />} href="/jobs" />
      <StatCard label="High Matches" value={stats.high_matches} icon={<Target className="h-5 w-5" />} href="/jobs?filter=high-match" />
      <StatCard label="Walk-ins Today" value={stats.walk_ins_today} icon={<Users className="h-5 w-5" />} href="/walk-ins?tab=today" />
      <StatCard
        label="Avg Match Score"
        value={`${Math.round(stats.average_match_score)}%`}
        icon={<TrendingUp className="h-5 w-5" />}
      />
      <StatCard label="New Today" value={stats.new_jobs_today} icon={<Briefcase className="h-5 w-5" />} />
      <StatCard label="Remote Jobs" value={stats.remote_jobs} icon={<MapPin className="h-5 w-5" />} href="/jobs?work_mode=remote" />
      <StatCard label="Hybrid Jobs" value={stats.hybrid_jobs} icon={<MapPin className="h-5 w-5" />} href="/jobs?work_mode=hybrid" />
      <StatCard label="Applications" value={stats.total_applications} icon={<ClipboardList className="h-5 w-5" />} href="/applications" />
      <StatCard label="Ready to Apply" value={stats.ready_to_apply} icon={<Briefcase className="h-5 w-5" />} href="/applications?status=ready_to_apply" />
      <StatCard label="Interviews" value={stats.interviews} icon={<Users className="h-5 w-5" />} href="/applications?status=interview_scheduled" />
      <StatCard label="Offers" value={stats.offers} icon={<TrendingUp className="h-5 w-5" />} href="/applications?status=offer_received" />
      <StatCard label="Rejections" value={stats.rejections} icon={<XCircle className="h-5 w-5" />} href="/applications?status=rejected" />
      <StatCard label="Favorites" value={stats.favorites} icon={<Star className="h-5 w-5" />} href="/applications?favorites_only=true" />
      <StatCard label="Ready to Submit" value={stats.ready_to_submit} icon={<ClipboardList className="h-5 w-5" />} href="/review-assistant" />
      <StatCard label="Under Review" value={stats.applications_under_review} icon={<ClipboardList className="h-5 w-5" />} href="/review-assistant" />
      <StatCard label="Submitted Today" value={stats.submitted_today} icon={<TrendingUp className="h-5 w-5" />} />
      <StatCard label="Validation Failures" value={stats.validation_failures} icon={<XCircle className="h-5 w-5" />} />
      <StatCard label="Avg Readiness" value={`${Math.round(stats.average_readiness_score)}%`} icon={<Target className="h-5 w-5" />} href="/review-assistant" />
      <StatCard
        label="Profile Complete"
        value={`${Math.round(stats.profile_completeness)}%`}
        icon={<Users className="h-5 w-5" />}
        href="/profile"
      />
    </div>
  );
}
