import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Upload, FileText, CheckCircle, Trash2, Download } from 'lucide-react';
import { useResumes, useUploadResume, useActivateResume, useDeleteResume } from '@/hooks';
import { resumesService } from '@/services';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState, ErrorState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ConfirmDialog } from '@/components/ui/Modal';
import { useToast } from '@/contexts/ToastContext';
import { formatDate, formatFileSize, parseApiError } from '@/utils';

export default function ResumesPage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const { data, isLoading, error, refetch } = useResumes({ page: 1, size: 50 });
  const uploadMutation = useUploadResume();
  const activateMutation = useActivateResume();
  const deleteMutation = useDeleteResume();
  const { addToast } = useToast();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await uploadMutation.mutateAsync(file);
      addToast('Resume uploaded', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
    e.target.value = '';
  };

  const handleDownload = async (id: number, filename: string) => {
    try {
      const { data: blob } = await resumesService.download(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Resumes</h1>
          <p className="mt-1 text-sm text-slate-500">Manage your master resumes and versions</p>
        </div>
        <input ref={fileRef} type="file" accept=".pdf,.doc,.docx" className="hidden" onChange={handleUpload} />
        <Button onClick={() => fileRef.current?.click()} loading={uploadMutation.isPending}>
          <Upload className="h-4 w-4" /> Upload resume
        </Button>
      </div>

      {!data?.items.length ? (
        <EmptyState
          title="No resumes yet"
          description="Upload your first resume to enable AI job matching."
          actionLabel="Upload resume"
          onAction={() => fileRef.current?.click()}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((resume) => (
            <Card key={resume.id}>
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-brand-50 p-2 dark:bg-brand-900/30">
                  <FileText className="h-6 w-6 text-brand-600" />
                </div>
                <div className="min-w-0 flex-1">
                  <Link to={`/resumes/${resume.id}`} className="truncate font-semibold hover:text-brand-600">
                    {resume.filename}
                  </Link>
                  <p className="text-xs text-slate-500">{formatFileSize(resume.file_size)} ┬╖ v{resume.version}</p>
                  <p className="text-xs text-slate-500">{formatDate(resume.created_at)}</p>
                  {resume.is_active && <Badge variant="success" className="mt-2">Active</Badge>}
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {!resume.is_active && (
                  <Button
                    size="sm"
                    variant="outline"
                    loading={activateMutation.isPending}
                    onClick={() => activateMutation.mutate(resume.id, { onSuccess: () => addToast('Active resume updated', 'success') })}
                  >
                    <CheckCircle className="h-3.5 w-3.5" /> Set active
                  </Button>
                )}
                <Button size="sm" variant="outline" onClick={() => handleDownload(resume.id, resume.filename)}>
                  <Download className="h-3.5 w-3.5" />
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setDeleteId(resume.id)}>
                  <Trash2 className="h-3.5 w-3.5 text-red-500" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={deleteId !== null}
        onClose={() => setDeleteId(null)}
        title="Delete resume"
        message="This action cannot be undone."
        confirmLabel="Delete"
        loading={deleteMutation.isPending}
        onConfirm={() => {
          if (deleteId) {
            deleteMutation.mutate(deleteId, {
              onSuccess: () => {
                addToast('Resume deleted', 'success');
                setDeleteId(null);
              },
              onError: (err) => addToast(parseApiError(err), 'error'),
            });
          }
        }}
      />
    </div>
  );
}
