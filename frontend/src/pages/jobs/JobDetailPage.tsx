import { useMemo, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ExternalLink, FileText, Mail, ArrowLeft, Bookmark, Mic } from 'lucide-react';
import {
  useJob,
  useMatchJob,
  useGenerateTailoredResume,
  useTailoredResume,
  useGenerateCoverLetter,
  useCoverLetter,
  useCoverLetterHistory,
  useCoverLetterTemplates,
  useResumes,
  useTailoredResumeHistory,
  useCreateApplication,
  useGenerateInterview,
  useInterviewPreparation,
} from '@/hooks';
import { useBookmarksStore } from '@/store';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState, EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge, MatchScoreBadge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { parseApiError, formatDate, formatDateTime } from '@/utils';
import { useToast } from '@/contexts/ToastContext';
import { coverLettersService, resumeTailoringService } from '@/services';
import { CoverLetterEditor } from '@/components/cover-letters/CoverLetterEditor';
import { CoverLetterPreview } from '@/components/cover-letters/CoverLetterPreview';
import { CoverLetterVersionHistory } from '@/components/cover-letters/CoverLetterVersionHistory';
import { DownloadDialog } from '@/components/cover-letters/DownloadDialog';
import { GenerationProgressIndicator } from '@/components/cover-letters/GenerationProgressIndicator';
import { TemplateSelector } from '@/components/cover-letters/TemplateSelector';
import { Select } from '@/components/ui/Input';

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const jobId = Number(id);
  const navigate = useNavigate();
  const { data: job, isLoading, error, refetch } = useJob(jobId);
  const { data: match, isLoading: matchLoading } = useMatchJob(jobId, !!job);
  const { isBookmarked, toggleBookmark } = useBookmarksStore();
  const { addToast } = useToast();
  const createApplicationMutation = useCreateApplication();
  const generateMutation = useGenerateTailoredResume();
  const [generationOpen, setGenerationOpen] = useState(false);
  const [coverLetterOpen, setCoverLetterOpen] = useState(false);
  const [downloadDialogOpen, setDownloadDialogOpen] = useState(false);
  const [tailoredResumeId, setTailoredResumeId] = useState<number | null>(null);
  const [coverLetterId, setCoverLetterId] = useState<number | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx' | 'markdown' | 'html'>('pdf');
  const [selectedCoverLetterFormat, setSelectedCoverLetterFormat] = useState<'pdf' | 'docx' | 'markdown' | 'html'>('pdf');
  const [useTailoredOnApply, setUseTailoredOnApply] = useState(true);
  const [useCoverLetterOnApply, setUseCoverLetterOnApply] = useState(true);
  const [editedCoverLetter, setEditedCoverLetter] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [selectedTailoredResumeId, setSelectedTailoredResumeId] = useState<number | null>(null);
  const [selectedCoverLetterId, setSelectedCoverLetterId] = useState<number | null>(null);
  const { data: resumes } = useResumes({ page: 1, size: 50 });
  const { data: tailoredHistory } = useTailoredResumeHistory(1, 50);

  const { data: tailoredResume } = useTailoredResume(
    tailoredResumeId ?? 0,
    Boolean(tailoredResumeId),
    tailoredResumeId ? 2000 : false,
  );
  const generationStatus = tailoredResume?.status ?? (generateMutation.isPending ? 'queued' : null);
  const generationDone = generationStatus === 'completed';
  const generationFailed = generationStatus === 'failed';
  const progressLabel = useMemo(() => {
    if (generationStatus === 'queued') return 'Queued';
    if (generationStatus === 'processing') return 'Generating ATS-tailored content';
    if (generationStatus === 'completed') return 'Completed';
    if (generationStatus === 'failed') return 'Failed';
    return 'Preparing';
  }, [generationStatus]);
  const generateCoverLetterMutation = useGenerateCoverLetter();
  const generateInterviewMutation = useGenerateInterview();
  const [interviewPrepId, setInterviewPrepId] = useState<number | null>(null);
  const [interviewPrepOpen, setInterviewPrepOpen] = useState(false);
  const { data: interviewPreparation } = useInterviewPreparation(interviewPrepId ?? 0, Boolean(interviewPrepId), interviewPrepId ? 2000 : false);
  const { data: generatedCoverLetter } = useCoverLetter(coverLetterId ?? 0, Boolean(coverLetterId), coverLetterId ? 2000 : false);
  const { data: coverLetterHistory } = useCoverLetterHistory(1, 10);
  const { data: coverLetterTemplates } = useCoverLetterTemplates();
  const coverLetterStatus = generatedCoverLetter?.status ?? (generateCoverLetterMutation.isPending ? 'queued' : null);
  const coverLetterDone = coverLetterStatus === 'completed';
  const coverLetterFailed = coverLetterStatus === 'failed';

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;
  if (!job) return <EmptyState title="Job not found" actionLabel="Browse jobs" onAction={() => window.history.back()} />;

  const bookmarked = isBookmarked(job.id);

  const handlePrepareApplication = async () => {
    try {
      await createApplicationMutation.mutateAsync({
        job_id: job.id,
        company_name: job.company ?? 'Unknown',
        job_title: job.title,
        apply_url: job.apply_url,
        selected_resume_id: selectedResumeId,
        selected_tailored_resume_id: selectedTailoredResumeId ?? (useTailoredOnApply && tailoredResume ? tailoredResume.id : null),
        selected_cover_letter_id: selectedCoverLetterId ?? (useCoverLetterOnApply && generatedCoverLetter ? generatedCoverLetter.id : null),
        status: 'ready_to_apply',
        source: job.source ?? 'jobs',
      });
      addToast('Application prepared and saved as Ready to Apply', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleApply = async () => {
    await handlePrepareApplication();
    if (job.apply_url) {
      window.open(job.apply_url, '_blank', 'noopener,noreferrer');
    }
    addToast('Application prepared and opened for manual apply', 'success');
  };

  const handleGenerateCoverLetter = async () => {
    try {
      setCoverLetterOpen(true);
      const result = await generateCoverLetterMutation.mutateAsync(job.id);
      setCoverLetterId(result.data.cover_letter_id);
      addToast(result.data.cached ? 'Using cached cover letter for this job' : 'Cover letter generation started', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
      setCoverLetterOpen(false);
    }
  };

  const handleDownloadCoverLetter = async () => {
    if (!generatedCoverLetter) return;
    try {
      const { data: blob } = await coverLettersService.download(generatedCoverLetter.id, selectedCoverLetterFormat);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cover_letter_job_${job.id}.${selectedCoverLetterFormat === 'markdown' ? 'md' : selectedCoverLetterFormat}`;
      a.click();
      URL.revokeObjectURL(url);
      setDownloadDialogOpen(false);
      addToast('Cover letter downloaded', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleGenerateResume = async () => {
    try {
      setGenerationOpen(true);
      const result = await generateMutation.mutateAsync(job.id);
      setTailoredResumeId(result.data.tailored_resume_id);
      if (result.data.cached) {
        addToast('Using cached tailored resume for this job', 'success');
      } else {
        addToast('Resume generation started', 'success');
      }
    } catch (err) {
      addToast(parseApiError(err), 'error');
      setGenerationOpen(false);
    }
  };

  const handleGenerateInterview = async () => {
    try {
      setInterviewPrepOpen(true);
      const result = await generateInterviewMutation.mutateAsync({ jobId: job.id });
      setInterviewPrepId(result.data.preparation_id);
      addToast(result.data.cached ? 'Using cached interview preparation' : 'Interview preparation started', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
      setInterviewPrepOpen(false);
    }
  };

  const interviewPrepStatus = interviewPreparation?.status ?? (generateInterviewMutation.isPending ? 'queued' : null);
  const interviewPrepDone = interviewPrepStatus === 'completed';
  const interviewPrepFailed = interviewPrepStatus === 'failed';

  const handleDownloadTailored = async () => {
    if (!tailoredResume) return;
    try {
      const { data: blob } = await resumeTailoringService.download(tailoredResume.id, selectedFormat);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tailored_resume_job_${job.id}.${selectedFormat === 'markdown' ? 'md' : selectedFormat}`;
      a.click();
      URL.revokeObjectURL(url);
      addToast('Tailored resume downloaded', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link to="/jobs" className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
        <ArrowLeft className="h-4 w-4" /> Back to jobs
      </Link>

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-2 flex flex-wrap gap-2">
              {match && <MatchScoreBadge score={match.score} category={match.category} />}
              {job.work_mode && <Badge variant="outline">{job.work_mode}</Badge>}
              {job.employment_type && <Badge variant="outline">{job.employment_type}</Badge>}
            </div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{job.title}</h1>
            <p className="mt-1 text-lg text-slate-600 dark:text-slate-400">{job.company}</p>
            <p className="mt-1 text-sm text-slate-500">{job.location}</p>
            {job.salary && <p className="mt-2 font-medium text-emerald-600">{job.salary}</p>}
          </div>
          <button
            onClick={() => toggleBookmark({ id: job.id, title: job.title, company: job.company ?? 'Unknown' })}
            className="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <Bookmark className={`h-6 w-6 ${bookmarked ? 'fill-brand-500 text-brand-500' : 'text-slate-400'}`} />
          </button>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <Button variant="outline" onClick={handlePrepareApplication} loading={createApplicationMutation.isPending}>
            Prepare Application
          </Button>
          <Button onClick={handleApply}>
            Apply <ExternalLink className="h-4 w-4" />
          </Button>
          <Button variant="outline" onClick={handleGenerateResume} loading={generateMutation.isPending}>
            <FileText className="h-4 w-4" /> Generate Resume
          </Button>
          <Button variant="outline" onClick={handleGenerateCoverLetter} loading={generateCoverLetterMutation.isPending}>
            <Mail className="h-4 w-4" /> Generate Cover Letter
          </Button>
          <Button variant="outline" onClick={handleGenerateInterview} loading={generateInterviewMutation.isPending}>
            <Mic className="h-4 w-4" /> Prepare Interview
          </Button>
        </div>
      </Card>
      <Card>
        <h2 className="mb-4 text-lg font-semibold">Application Preparation</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          <Select
            value={String(selectedResumeId ?? '')}
            onChange={(event) => setSelectedResumeId(event.target.value ? Number(event.target.value) : null)}
            options={[
              { value: '', label: 'Select Resume' },
              ...(resumes?.items ?? []).map((resume) => ({
                value: String(resume.id),
                label: `Resume #${resume.id} v${resume.version}${resume.is_active ? ' (active)' : ''}`,
              })),
            ]}
          />
          <Select
            value={String(selectedTailoredResumeId ?? '')}
            onChange={(event) => setSelectedTailoredResumeId(event.target.value ? Number(event.target.value) : null)}
            options={[
              { value: '', label: 'Select Tailored Resume' },
              ...(tailoredHistory?.items ?? []).map((item) => ({
                value: String(item.tailored_resume_id ?? ''),
                label: `Tailored #${item.tailored_resume_id ?? 'N/A'} - ${item.status}`,
              })),
            ]}
          />
          <Select
            value={String(selectedCoverLetterId ?? '')}
            onChange={(event) => setSelectedCoverLetterId(event.target.value ? Number(event.target.value) : null)}
            options={[
              { value: '', label: 'Select Cover Letter' },
              ...(coverLetterHistory?.items ?? []).map((item) => ({
                value: String(item.generated_cover_letter_id ?? ''),
                label: `Cover Letter #${item.generated_cover_letter_id ?? 'N/A'} - ${item.status}`,
              })),
            ]}
          />
        </div>
      </Card>

      <Modal
        open={generationOpen}
        onClose={() => setGenerationOpen(false)}
        title="AI Resume Tailoring"
        footer={
          generationDone ? (
            <>
              <Button variant="outline" onClick={() => setGenerationOpen(false)}>Close</Button>
              <Button onClick={handleDownloadTailored}>Download</Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setGenerationOpen(false)}>Close</Button>
          )
        }
      >
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-sm font-medium">Generation progress</p>
            <div className="mt-2 h-2 w-full overflow-hidden rounded bg-slate-200 dark:bg-slate-700">
              <div
                className="h-2 rounded bg-brand-600 transition-all"
                style={{ width: generationDone ? '100%' : generationStatus === 'processing' ? '65%' : generationStatus === 'failed' ? '100%' : '30%' }}
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">{progressLabel}</p>
          </div>

          {generationFailed && (
            <p className="text-sm text-red-600 dark:text-red-400">
              Resume generation failed. Please try again.
            </p>
          )}

          {generationDone && tailoredResume && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <Card>
                  <p className="text-xs text-slate-500">ATS Score</p>
                  <p className="text-xl font-bold">{tailoredResume.ats_score ?? 'ΓÇö'}</p>
                </Card>
                <Card>
                  <p className="text-xs text-slate-500">Generated At</p>
                  <p className="text-sm font-medium">{formatDateTime(tailoredResume.generated_at)}</p>
                </Card>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium">Preview</p>
                <div className="max-h-52 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs dark:border-slate-700 dark:bg-slate-900">
                  <pre className="whitespace-pre-wrap">{tailoredResume.markdown_content ?? 'No preview available.'}</pre>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {(['pdf', 'docx', 'markdown', 'html'] as const).map((fmt) => (
                  <Button key={fmt} size="sm" variant={selectedFormat === fmt ? 'primary' : 'outline'} onClick={() => setSelectedFormat(fmt)}>
                    {fmt.toUpperCase()}
                  </Button>
                ))}
              </div>

              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={useTailoredOnApply}
                  onChange={(e) => setUseTailoredOnApply(e.target.checked)}
                />
                Use this tailored resume when applying from this page
              </label>
            </>
          )}
        </div>
      </Modal>

      <Modal
        open={coverLetterOpen}
        onClose={() => setCoverLetterOpen(false)}
        title="AI Cover Letter Generation"
        footer={
          coverLetterDone ? (
            <>
              <Button variant="outline" onClick={() => setCoverLetterOpen(false)}>
                Close
              </Button>
              <Button variant="outline" onClick={() => setDownloadDialogOpen(true)}>
                Download
              </Button>
              <Button onClick={() => addToast('Cover letter saved for this application', 'success')}>Save</Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setCoverLetterOpen(false)}>
              Close
            </Button>
          )
        }
      >
        <div className="space-y-4">
          <GenerationProgressIndicator status={coverLetterStatus} />
          <TemplateSelector
            templates={coverLetterTemplates ?? []}
            selectedTemplateId={selectedTemplateId}
            onSelect={setSelectedTemplateId}
          />
          {coverLetterFailed && <p className="text-sm text-red-600 dark:text-red-400">Cover letter generation failed. Please try again.</p>}
          {coverLetterDone && generatedCoverLetter && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <Card>
                  <p className="text-xs text-slate-500">Quality Score</p>
                  <p className="text-xl font-bold">{generatedCoverLetter.quality_score ?? 'ΓÇö'}</p>
                </Card>
                <Card>
                  <p className="text-xs text-slate-500">Generated At</p>
                  <p className="text-sm font-medium">{formatDateTime(generatedCoverLetter.generated_at)}</p>
                </Card>
              </div>
              <CoverLetterPreview content={editedCoverLetter || generatedCoverLetter.markdown_content} />
              <CoverLetterEditor
                value={editedCoverLetter || generatedCoverLetter.markdown_content || ''}
                onChange={setEditedCoverLetter}
              />
              <CoverLetterVersionHistory items={coverLetterHistory?.items ?? []} />
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={useCoverLetterOnApply}
                  onChange={(e) => setUseCoverLetterOnApply(e.target.checked)}
                />
                Use this cover letter when applying from this page
              </label>
            </>
          )}
        </div>
      </Modal>

      <DownloadDialog
        open={downloadDialogOpen}
        onClose={() => setDownloadDialogOpen(false)}
        selectedFormat={selectedCoverLetterFormat}
        onFormatChange={setSelectedCoverLetterFormat}
        onDownload={handleDownloadCoverLetter}
      />

      <Modal
        open={interviewPrepOpen}
        onClose={() => setInterviewPrepOpen(false)}
        title="AI Interview Preparation"
      >
        <div className="space-y-4">
          <GenerationProgressIndicator status={interviewPrepStatus} />
          {interviewPrepFailed && <p className="text-sm text-red-600 dark:text-red-400">Interview preparation failed. Please try again.</p>}
          {interviewPrepDone && interviewPreparation && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <Card>
                  <p className="text-xs text-slate-500">Readiness Score</p>
                  <p className="text-xl font-bold">{interviewPreparation.readiness_score ?? '—'}</p>
                </Card>
                <Card>
                  <p className="text-xs text-slate-500">Estimated Duration</p>
                  <p className="text-sm font-medium">{interviewPreparation.estimated_duration_minutes ?? '—'} min</p>
                </Card>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button onClick={() => navigate(`/interview-prep/${interviewPreparation.id}`)}>Preview Preparation</Button>
                <Button variant="secondary" onClick={() => navigate(`/interview-prep/${interviewPreparation.id}/practice`)}>Start Practice</Button>
              </div>
            </>
          )}
        </div>
      </Modal>

      {match && !matchLoading && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">AI Match Analysis</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">{match.reasoning}</p>
          {match.matched_skills.length > 0 && (
            <div className="mt-4">
              <p className="mb-2 text-sm font-medium">Matched skills</p>
              <div className="flex flex-wrap gap-1">
                {match.matched_skills.map((s) => (
                  <Badge key={s} variant="success">{s}</Badge>
                ))}
              </div>
            </div>
          )}
          {match.missing_skills.length > 0 && (
            <div className="mt-4">
              <p className="mb-2 text-sm font-medium">Skills to develop</p>
              <div className="flex flex-wrap gap-1">
                {match.missing_skills.map((s) => (
                  <Badge key={s} variant="warning">{s}</Badge>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Job Description</h2>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600 dark:text-slate-400">
          {job.description ?? 'No description available.'}
        </p>
      </Card>

      <Card>
        <h2 className="mb-4 text-lg font-semibold">Details</h2>
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Experience</dt><dd className="font-medium">{job.experience ?? 'ΓÇö'}</dd></div>
          <div><dt className="text-slate-500">Source</dt><dd className="font-medium">{job.source ?? 'ΓÇö'}</dd></div>
          <div><dt className="text-slate-500">Posted</dt><dd className="font-medium">{formatDate(job.posted_date)}</dd></div>
          <div><dt className="text-slate-500">Updated</dt><dd className="font-medium">{formatDate(job.updated_at)}</dd></div>
        </dl>
        {job.skills && job.skills.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-sm text-slate-500">Required skills</p>
            <div className="flex flex-wrap gap-1">
              {job.skills.map((s) => <Badge key={s}>{s}</Badge>)}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
