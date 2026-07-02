import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle } from 'lucide-react';
import { useResumes, useActivateResume } from '@/hooks';
import { resumesService } from '@/services';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/contexts/ToastContext';
import { formatDate, formatFileSize, parseApiError } from '@/utils';

export default function ResumeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const resumeId = Number(id);
  const { data, isLoading } = useResumes({ page: 1, size: 100 });
  const activateMutation = useActivateResume();
  const { addToast } = useToast();

  const resume = data?.items.find((r) => r.id === resumeId);

  const handleDownload = async () => {
    if (!resume) return;
    try {
      const { data: blob } = await resumesService.download(resume.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = resume.filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  if (isLoading) return <PageLoader />;
  if (!resume) return <EmptyState title="Resume not found" />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link to="/resumes" className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
        <ArrowLeft className="h-4 w-4" /> Back to resumes
      </Link>

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{resume.filename}</h1>
            <p className="mt-1 text-sm text-slate-500">
              {resume.content_type} ┬╖ {formatFileSize(resume.file_size)} ┬╖ Version {resume.version}
            </p>
            {resume.is_active && <Badge variant="success" className="mt-2">Active resume</Badge>}
          </div>
          <div className="flex gap-2">
            {!resume.is_active && (
              <Button
                variant="outline"
                loading={activateMutation.isPending}
                onClick={() =>
                  activateMutation.mutate(resume.id, {
                    onSuccess: () => addToast('Set as active resume', 'success'),
                  })
                }
              >
                <CheckCircle className="h-4 w-4" /> Set active
              </Button>
            )}
            <Button onClick={handleDownload}>
              <Download className="h-4 w-4" /> Download
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Details</h2>
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Uploaded</dt><dd>{formatDate(resume.created_at)}</dd></div>
          <div><dt className="text-slate-500">Last updated</dt><dd>{formatDate(resume.updated_at)}</dd></div>
          <div><dt className="text-slate-500">Storage path</dt><dd className="truncate font-mono text-xs">{resume.storage_path}</dd></div>
        </dl>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Version History</h2>
        <div className="space-y-2">
          {data?.items
            .sort((a, b) => b.version - a.version)
            .map((v) => (
              <div
                key={v.id}
                className={`flex items-center justify-between rounded-lg border p-3 ${v.id === resume.id ? 'border-brand-300 bg-brand-50 dark:border-brand-700 dark:bg-brand-900/20' : 'border-slate-200 dark:border-slate-700'}`}
              >
                <div>
                  <p className="font-medium">Version {v.version}</p>
                  <p className="text-xs text-slate-500">{formatDate(v.created_at)}</p>
                </div>
                {v.is_active && <Badge variant="success">Active</Badge>}
              </div>
            ))}
        </div>
      </Card>
    </div>
  );
}
