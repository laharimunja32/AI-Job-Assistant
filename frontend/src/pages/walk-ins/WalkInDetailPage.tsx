import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, MapPin } from 'lucide-react';
import { useWalkIn } from '@/hooks';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState, EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { parseApiError, formatDate } from '@/utils';

export default function WalkInDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: walkIn, isLoading, error, refetch } = useWalkIn(Number(id));

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  if (!walkIn) return <EmptyState title="Walk-in not found" />;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link to="/walk-ins" className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
        <ArrowLeft className="h-4 w-4" /> Back to walk-ins
      </Link>

      <Card>
        <div className="mb-2 flex gap-2">
          <Badge variant={walkIn.event_status === 'Today' ? 'danger' : 'info'}>{walkIn.event_status}</Badge>
          <Badge variant="success">AI Matched</Badge>
        </div>
        <h1 className="text-2xl font-bold">{walkIn.job_role}</h1>
        <p className="mt-1 text-lg text-slate-600">{walkIn.company_name}</p>
        {walkIn.registration_url && (
          <a href={walkIn.registration_url} target="_blank" rel="noopener noreferrer" className="mt-4 inline-block">
            <Button>Register <ExternalLink className="h-4 w-4" /></Button>
          </a>
        )}
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Venue</h2>
        <p className="flex items-start gap-2 text-slate-600">
          <MapPin className="mt-0.5 h-5 w-5 shrink-0" />
          {[walkIn.venue, walkIn.city, walkIn.state].filter(Boolean).join(', ') || 'Venue TBA'}
        </p>
        <div className="mt-4 flex h-48 items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 text-sm text-slate-400 dark:border-slate-700 dark:bg-slate-800">
          Map integration ΓÇö coming soon
        </div>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Schedule</h2>
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Date</dt><dd className="font-medium">{formatDate(walkIn.walk_in_date)}</dd></div>
          <div><dt className="text-slate-500">Time</dt><dd className="font-medium">{walkIn.walk_in_time ?? 'ΓÇö'}</dd></div>
          <div><dt className="text-slate-500">Registration deadline</dt><dd className="font-medium">{formatDate(walkIn.registration_deadline)}</dd></div>
        </dl>
      </Card>

      {walkIn.eligibility && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Eligibility</h2>
          <p className="text-sm text-slate-600">{walkIn.eligibility}</p>
          <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
            {walkIn.degree && <div><dt className="text-slate-500">Degree</dt><dd>{walkIn.degree}</dd></div>}
            {walkIn.branch && <div><dt className="text-slate-500">Branch</dt><dd>{walkIn.branch}</dd></div>}
            {walkIn.passout_year && <div><dt className="text-slate-500">Passout year</dt><dd>{walkIn.passout_year}</dd></div>}
            {walkIn.experience_required && <div><dt className="text-slate-500">Experience</dt><dd>{walkIn.experience_required}</dd></div>}
          </dl>
        </Card>
      )}

      {walkIn.job_description && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Description</h2>
          <p className="whitespace-pre-wrap text-sm text-slate-600">{walkIn.job_description}</p>
        </Card>
      )}

      {walkIn.documents_required && walkIn.documents_required.length > 0 && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Documents Required</h2>
          <ul className="list-inside list-disc text-sm text-slate-600">
            {walkIn.documents_required.map((d) => <li key={d}>{d}</li>)}
          </ul>
        </Card>
      )}
    </div>
  );
}
