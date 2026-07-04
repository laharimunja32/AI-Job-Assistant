import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import { CoverLetterEditor, CoverLetterPreview, DownloadButtons } from '@/components/cover-letter-generator';
import { useCoverLetterDetail, useDeleteCoverLetter, useUpdateCoverLetter } from '@/hooks/useCoverLetterGenerator';
import { coverLetterGeneratorService } from '@/services';
import { Badge, Button, ConfirmDialog, ErrorState } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';

export default function CoverLetterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const letterId = Number(id);
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data, isLoading, error, refetch } = useCoverLetterDetail(letterId, Boolean(letterId));
  const updateMutation = useUpdateCoverLetter();
  const deleteMutation = useDeleteCoverLetter();

  const [editedContent, setEditedContent] = useState('');
  const [isDirty, setIsDirty] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [downloading, setDownloading] = useState<'pdf' | 'docx' | null>(null);

  useEffect(() => {
    if (data?.generated_letter) {
      setEditedContent(data.generated_letter);
      setIsDirty(false);
    }
  }, [data?.generated_letter]);

  const handleSave = async () => {
    if (editedContent.trim().length < 10) {
      addToast('Cover letter must be at least 10 characters', 'error');
      return;
    }
    try {
      await updateMutation.mutateAsync({ id: letterId, generated_letter: editedContent });
      addToast('Changes saved', 'success');
      setIsDirty(false);
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleDownload = async (format: 'pdf' | 'docx') => {
    setDownloading(format);
    try {
      const { data: blob } = await coverLetterGeneratorService.download(letterId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cover_letter_${letterId}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      addToast(`Downloaded ${format.toUpperCase()}`, 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    } finally {
      setDownloading(null);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(letterId);
      addToast('Cover letter deleted', 'success');
      navigate('/cover-letter-generator/history');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  if (isLoading) return <PageLoader />;
  if (error || !data) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link to="/cover-letter-generator/history" className="text-slate-500 hover:text-slate-700">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {data.job_title ?? 'Cover Letter'}
            </h1>
            {data.company_name && <p className="text-sm text-slate-500">{data.company_name}</p>}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="default">{data.template_name}</Badge>
          <Badge variant="info">{data.tone}</Badge>
          <Badge variant="success">{data.length}</Badge>
          <DownloadButtons onDownload={handleDownload} downloading={downloading} />
          <Button
            variant="outline"
            onClick={handleSave}
            disabled={!isDirty || updateMutation.isPending}
            className="gap-2"
          >
            <Save className="h-4 w-4" />
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
          <Button variant="outline" onClick={() => setShowDelete(true)} className="gap-2 text-rose-600">
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <CoverLetterEditor
          value={editedContent}
          onChange={(value) => {
            setEditedContent(value);
            setIsDirty(value !== data.generated_letter);
          }}
        />
        <CoverLetterPreview content={editedContent} />
      </div>

      <ConfirmDialog
        open={showDelete}
        title="Delete cover letter?"
        message="This will permanently remove this cover letter and its downloads."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onClose={() => setShowDelete(false)}
      />
    </div>
  );
}
