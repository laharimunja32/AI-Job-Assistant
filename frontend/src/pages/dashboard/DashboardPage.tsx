import { RefreshCw } from 'lucide-react';
import { useDashboard, useRefreshDashboard } from '@/hooks';
import { DashboardStats } from '@/components/dashboard/StatCard';
import { DashboardSection } from '@/components/dashboard/DashboardSection';
import { JobCard, JobListGrid } from '@/components/jobs/JobCard';
import { WalkInCard } from '@/components/walk-ins/WalkInCard';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState } from '@/components/ui/EmptyState';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { parseApiError, formatDate } from '@/utils';
import { useToast } from '@/contexts/ToastContext';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard(1, 6);
  const refreshMutation = useRefreshDashboard();
  const { addToast } = useToast();

  const handleRefresh = async () => {
    try {
      const result = await refreshMutation.mutateAsync();
      addToast(
        `Refreshed ${result.data.matches_computed} matches (avg ${Math.round(result.data.average_score)}%)`,
        'success',
      );
      refetch();
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  if (isLoading) return <PageLoader />;
  if (error || !data) {
    return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  }

  const cityChartData = data.jobs_by_city.cities.slice(0, 8).map((c) => ({
    name: c.city,
    jobs: c.count,
  }));

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Your Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">
            Personalized jobs and walk-ins ΓÇö no search required
          </p>
        </div>
        <Button onClick={handleRefresh} loading={refreshMutation.isPending} variant="outline">
          <RefreshCw className="h-4 w-4" /> Refresh matches
        </Button>
      </div>

      <DashboardStats stats={data.statistics} />

      <DashboardSection title="Recruitment Monitoring" viewAllHref="/recruitment-emails">
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          <Card><p className="text-xs text-slate-500">Upcoming Assessments</p><p className="text-xl font-bold">{data.recruitment_summary.upcoming_assessments}</p></Card>
          <Card><p className="text-xs text-slate-500">Upcoming Interviews</p><p className="text-xl font-bold">{data.recruitment_summary.upcoming_interviews}</p></Card>
          <Card><p className="text-xs text-slate-500">Offers</p><p className="text-xl font-bold">{data.recruitment_summary.offers}</p></Card>
          <Card><p className="text-xs text-slate-500">Rejections</p><p className="text-xl font-bold">{data.recruitment_summary.rejections}</p></Card>
          <Card><p className="text-xs text-slate-500">Unread Emails</p><p className="text-xl font-bold">{data.recruitment_summary.unread_recruitment_emails}</p></Card>
          <Card><p className="text-xs text-slate-500">Today's Deadlines</p><p className="text-xl font-bold">{data.recruitment_summary.todays_deadlines}</p></Card>
        </div>
      </DashboardSection>

      <DashboardSection title="Browser Automation Status" viewAllHref="/browser-automation">
        <div className="grid gap-4 md:grid-cols-4">
          <Card><p className="text-xs text-slate-500">Active Sessions</p><p className="text-xl font-bold">{data.statistics.browser_active_sessions}</p></Card>
          <Card><p className="text-xs text-slate-500">Last Browser Activity</p><p className="text-sm font-medium">{data.statistics.browser_last_activity ?? 'ΓÇö'}</p></Card>
          <Card><p className="text-xs text-slate-500">Navigation Success Rate</p><p className="text-xl font-bold">{Math.round(data.statistics.browser_navigation_success_rate)}%</p></Card>
          <Card><p className="text-xs text-slate-500">Browser Status</p><p className="text-xl font-bold capitalize">{data.statistics.browser_status}</p></Card>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          <Card><p className="text-xs text-slate-500">Forms Detected</p><p className="text-xl font-bold">{data.statistics.forms_detected}</p></Card>
          <Card><p className="text-xs text-slate-500">Fields Filled</p><p className="text-xl font-bold">{data.statistics.fields_filled}</p></Card>
          <Card><p className="text-xs text-slate-500">Manual Fields Remaining</p><p className="text-xl font-bold">{data.statistics.manual_fields_remaining}</p></Card>
          <Card><p className="text-xs text-slate-500">Avg Fill Success Rate</p><p className="text-xl font-bold">{Math.round(data.statistics.average_fill_success_rate)}%</p></Card>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Card><p className="text-xs text-slate-500">Successful Uploads</p><p className="text-xl font-bold">{data.statistics.successful_uploads}</p></Card>
          <Card><p className="text-xs text-slate-500">Failed Uploads</p><p className="text-xl font-bold">{data.statistics.failed_uploads}</p></Card>
          <Card><p className="text-xs text-slate-500">Avg Upload Time</p><p className="text-xl font-bold">{Math.round(data.statistics.average_upload_time_ms)} ms</p></Card>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Card><p className="text-xs text-slate-500">Resume Upload Count</p><p className="text-xl font-bold">{data.statistics.resume_upload_count}</p></Card>
          <Card><p className="text-xs text-slate-500">Cover Letter Upload Count</p><p className="text-xl font-bold">{data.statistics.cover_letter_upload_count}</p></Card>
        </div>
      </DashboardSection>

      <DashboardSection title="Recent Applications" viewAllHref="/application-history">
        {data.recent_automation_applications.length > 0 ? (
          <div className="grid gap-3">
            {data.recent_automation_applications.map((app) => (
              <Card key={app.id}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{app.job_title}</p>
                    <p className="text-sm text-slate-500">{app.company_name}</p>
                  </div>
                  <Badge variant={app.status === 'completed' ? 'success' : 'outline'}>{app.status.replace(/_/g, ' ')}</Badge>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card><p className="text-sm text-slate-500">No browser applications yet. Start from Job Search or Saved Jobs.</p></Card>
        )}
      </DashboardSection>

      <DashboardSection title="Recent Saved Jobs" viewAllHref="/saved-jobs">
        {data.recent_saved_jobs.length > 0 ? (
          <div className="grid gap-3 md:grid-cols-2">
            {data.recent_saved_jobs.map((job) => (
              <Card key={job.id}>
                <p className="font-medium">{job.job_title}</p>
                <p className="text-sm text-slate-500">{job.company_name}</p>
                {job.location && <p className="mt-1 text-xs text-slate-400">{job.location}</p>}
              </Card>
            ))}
          </div>
        ) : (
          <Card><p className="text-sm text-slate-500">No saved jobs yet. Use Live Job Search to bookmark roles.</p></Card>
        )}
      </DashboardSection>

      <DashboardSection title="High Match Jobs" viewAllHref="/jobs?filter=high-match">
        {data.high_match_jobs.items.length > 0 ? (
          <JobListGrid>
            {data.high_match_jobs.items.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </JobListGrid>
        ) : (
          <Card><p className="text-sm text-slate-500">No high-match jobs yet. Complete your profile to improve matches.</p></Card>
        )}
      </DashboardSection>

      <DashboardSection title="Recommended for You" viewAllHref="/jobs">
        <JobListGrid>
          {data.recommended_jobs.items.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </JobListGrid>
      </DashboardSection>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="New Jobs" viewAllHref="/jobs?sort=newest">
          <JobListGrid>
            {data.new_jobs.items.slice(0, 3).map((job) => (
              <JobCard key={job.id} job={job} compact />
            ))}
          </JobListGrid>
        </DashboardSection>

        <DashboardSection title="Today's Walk-ins" viewAllHref="/walk-ins?tab=today">
          <div className="grid gap-4">
            {data.todays_walk_ins.items.length > 0 ? (
              data.todays_walk_ins.items.slice(0, 3).map((w) => <WalkInCard key={w.id} walkIn={w} showAiBadge />)
            ) : (
              <Card><p className="text-sm text-slate-500">No walk-ins scheduled for today.</p></Card>
            )}
          </div>
        </DashboardSection>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Recently Generated Cover Letters">
          <Card>
            {data.recent_cover_letters.length > 0 ? (
              <div className="space-y-2">
                {data.recent_cover_letters.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
                    <div>
                      <p className="font-medium">{item.company_name ?? `Job #${item.job_id}`} ┬╖ Version {item.cover_letter_version}</p>
                      <p className="text-xs text-slate-500">{formatDate(item.generated_at)}</p>
                    </div>
                    <Badge variant="info">Quality {item.quality_score ?? 'ΓÇö'}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No cover letters generated yet.</p>
            )}
          </Card>
        </DashboardSection>

        <DashboardSection title="Cover Letter History">
          <Card>
            {data.cover_letter_generation_history.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {data.cover_letter_generation_history.map((item) => (
                  <li key={item.id} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                    <p className="font-medium">{item.company_name ?? `Job #${item.job_id}`} ┬╖ {item.status}</p>
                    <p className="text-xs text-slate-500">{item.message ?? 'No details provided'}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No cover-letter generation history yet.</p>
            )}
          </Card>
        </DashboardSection>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Recently Used Templates">
          <Card>
            {data.recent_cover_letter_templates.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {data.recent_cover_letter_templates.map((item) => (
                  <li key={item.id} className="flex items-center justify-between rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                    <span>{item.name}</span>
                    <Badge variant={item.is_default ? 'success' : 'default'}>v{item.version}</Badge>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No templates used yet.</p>
            )}
          </Card>
        </DashboardSection>

        <DashboardSection title="Cover Letter Generation Statistics">
          <Card>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><p className="text-slate-500">Generated</p><p className="font-semibold">{data.cover_letter_statistics.total_generated}</p></div>
              <div><p className="text-slate-500">In Queue</p><p className="font-semibold">{data.cover_letter_statistics.queued_or_processing}</p></div>
              <div><p className="text-slate-500">Failed</p><p className="font-semibold">{data.cover_letter_statistics.failed}</p></div>
              <div><p className="text-slate-500">Cache Hits</p><p className="font-semibold">{data.cover_letter_statistics.cache_hits}</p></div>
            </div>
            <p className="mt-3 text-xs text-slate-500">Average quality score: {data.cover_letter_statistics.average_quality_score ?? 'ΓÇö'}</p>
          </Card>
        </DashboardSection>
      </div>

      <DashboardSection title="Interview Readiness" viewAllHref="/interview-prep/history">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card><p className="text-xs text-slate-500">Average Interview Score</p><p className="text-xl font-bold">{data.interview_statistics.average_readiness ?? '—'}</p></Card>
          <Card><p className="text-xs text-slate-500">Practice Sessions</p><p className="text-xl font-bold">{data.interview_statistics.practice_sessions}</p></Card>
          <Card><p className="text-xs text-slate-500">Questions Answered</p><p className="text-xl font-bold">{data.interview_statistics.questions_answered}</p></Card>
          <Card><p className="text-xs text-slate-500">Average Confidence</p><p className="text-xl font-bold">{data.interview_statistics.average_confidence ?? '—'}</p></Card>
        </div>
      </DashboardSection>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Recent Practice Sessions" viewAllHref="/interview-prep/history">
          <div className="space-y-3">
            {data.recent_interviews.length > 0 ? data.recent_interviews.map((item) => (
              <Card key={item.id} className="p-3">
                <p className="font-medium">{item.job_title ?? `Job #${item.job_id}`}</p>
                <p className="text-xs text-slate-500">{item.company_name ?? 'Company'} · Score {item.readiness_score ?? item.overall_score ?? '—'}</p>
              </Card>
            )) : <p className="text-sm text-slate-500">No practice sessions yet.</p>}
          </div>
        </DashboardSection>

        <DashboardSection title="Practice Progress">
          <Card className="p-4">
            <p className="text-sm text-slate-500">Weakest Skills</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {data.interview_statistics.weakest_topics.map((topic) => (
                <Badge key={topic.topic} variant="warning">{topic.topic.replace(/_/g, ' ')} ({topic.score})</Badge>
              ))}
            </div>
            <p className="mt-4 text-sm text-slate-500">Strongest Categories</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {data.interview_statistics.strongest_topics.map((topic) => (
                <Badge key={topic.topic} variant="success">{topic.topic.replace(/_/g, ' ')} ({topic.score})</Badge>
              ))}
            </div>
          </Card>
        </DashboardSection>
      </div>

      <DashboardSection title="Upcoming Walk-ins" viewAllHref="/walk-ins?tab=upcoming">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.upcoming_walk_ins.items.map((w) => (
            <WalkInCard key={w.id} walkIn={w} />
          ))}
        </div>
      </DashboardSection>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Remote Jobs" viewAllHref="/jobs?work_mode=remote">
          <JobListGrid>
            {data.remote_jobs.items.slice(0, 3).map((job) => (
              <JobCard key={job.id} job={job} compact />
            ))}
          </JobListGrid>
        </DashboardSection>

        <DashboardSection title="Hybrid Jobs" viewAllHref="/jobs?work_mode=hybrid">
          <JobListGrid>
            {data.hybrid_jobs.items.slice(0, 3).map((job) => (
              <JobCard key={job.id} job={job} compact />
            ))}
          </JobListGrid>
        </DashboardSection>
      </div>

      <DashboardSection title="Closing Soon" viewAllHref="/notifications">
        <Card>
          <div className="space-y-3">
            {data.closing_soon.items.length > 0 ? (
              data.closing_soon.items.map((item, i) => (
                <div key={`${item.type}-${item.id}-${i}`} className="flex items-center justify-between border-b border-slate-100 pb-3 last:border-0 dark:border-slate-800">
                  <div>
                    <p className="font-medium">{item.title ?? item.job_role}</p>
                    <p className="text-sm text-slate-500">{item.company ?? item.company_name}</p>
                  </div>
                  <Badge variant="warning">{item.type}</Badge>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">Nothing closing soon.</p>
            )}
          </div>
        </Card>
      </DashboardSection>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Recently Generated Resumes">
          <Card>
            {data.recent_tailored_resumes.length > 0 ? (
              <div className="space-y-2">
                {data.recent_tailored_resumes.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-lg border border-slate-200 p-3 text-sm dark:border-slate-700">
                    <div>
                      <p className="font-medium">Job #{item.job_id} ┬╖ Version {item.resume_version}</p>
                      <p className="text-xs text-slate-500">{formatDate(item.generated_at)}</p>
                    </div>
                    <Badge variant="info">ATS {item.ats_score ?? 'ΓÇö'}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No tailored resumes yet.</p>
            )}
          </Card>
        </DashboardSection>

        <DashboardSection title="Resume Generation History">
          <Card>
            {data.resume_generation_history.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {data.resume_generation_history.map((item) => (
                  <li key={item.id} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
                    <p className="font-medium">Job #{item.job_id} ┬╖ {item.status}</p>
                    <p className="text-xs text-slate-500">{item.message ?? 'No details provided'}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">No generation history yet.</p>
            )}
          </Card>
        </DashboardSection>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Resume ATS Insights">
          <Card>
            <p className="text-sm text-slate-500">Average ATS score</p>
            <p className="mt-1 text-2xl font-bold">{data.resume_ats_average ?? 'ΓÇö'}</p>
          </Card>
        </DashboardSection>

        <DashboardSection title="Improvement Suggestions">
          <Card>
            {data.resume_improvement_suggestions.length > 0 ? (
              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700 dark:text-slate-300">
                {data.resume_improvement_suggestions.map((tip, i) => (
                  <li key={`${tip}-${i}`}>{tip}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Generate a tailored resume to see suggestions.</p>
            )}
          </Card>
        </DashboardSection>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <DashboardSection title="Recently Added Companies" viewAllHref="/jobs">
          <Card>
            <ul className="space-y-2">
              {data.recent_companies.items.map((c) => (
                <li key={c.company_name} className="flex justify-between text-sm">
                  <span className="font-medium">{c.company_name}</span>
                  <span className="text-slate-500">{formatDate(c.latest_job_at)}</span>
                </li>
              ))}
            </ul>
          </Card>
        </DashboardSection>

        {cityChartData.length > 0 && (
          <DashboardSection title="Jobs by City">
            <Card>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={cityChartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="jobs" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </DashboardSection>
        )}
      </div>
    </div>
  );
}
