import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { History, ScanSearch } from 'lucide-react';
import { useAnalyzeResume, useResumes } from '@/hooks';
import { Button, Card, EmptyState, ErrorState, Input } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';

export default function ResumeOptimizerPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: resumesData, isLoading, error, refetch } = useResumes({ page: 1, size: 50 });
  const analyzeMutation = useAnalyzeResume();

  const [resumeId, setResumeId] = useState<number | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');

  const activeResume = resumesData?.items.find((r) => r.is_active) ?? resumesData?.items[0];
  const selectedResumeId = resumeId ?? activeResume?.id ?? null;

  const handleAnalyze = async () => {
    if (!selectedResumeId) {
      addToast('Please upload a resume first', 'error');
      return;
    }
    if (jobDescription.trim().length < 10) {
      addToast('Job description must be at least 10 characters', 'error');
      return;
    }
    try {
      const { data } = await analyzeMutation.mutateAsync({
        resume_id: selectedResumeId,
        job_description: jobDescription.trim(),
        job_title: jobTitle.trim() || undefined,
        company_name: companyName.trim() || undefined,
      });
      addToast('Resume analysis complete', 'success');
      navigate(`/resume-optimizer/${data.id}`);
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Resume Optimizer</h1>
          <p className="text-sm text-slate-500">Compare your resume against a job description, score ATS compatibility, and generate an improved version.</p>
        </div>
        <Link to="/resume-optimizer/history">
          <Button variant="outline" className="gap-2">
            <History className="h-4 w-4" />
            View History
          </Button>
        </Link>
      </div>

      {!resumesData?.items.length ? (
        <EmptyState
          title="No resume uploaded"
          description="Upload a master resume before running ATS optimization."
          actionLabel="Go to Resumes"
          onAction={() => navigate('/resumes')}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="space-y-4 p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">1. Select Resume</h2>
            <select
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800"
              value={selectedResumeId ?? ''}
              onChange={(e) => setResumeId(Number(e.target.value))}
            >
              {resumesData.items.map((resume) => (
                <option key={resume.id} value={resume.id}>
                  {resume.filename} {resume.is_active ? '(Active)' : ''}
                </option>
              ))}
            </select>

            <h2 className="pt-2 text-lg font-semibold text-slate-900 dark:text-slate-100">2. Job Details (optional)</h2>
            <Input placeholder="Job title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
            <Input placeholder="Company name" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />

            <h2 className="pt-2 text-lg font-semibold text-slate-900 dark:text-slate-100">3. Paste Job Description</h2>
            <textarea
              className="min-h-48 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800"
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />

            <Button onClick={handleAnalyze} disabled={analyzeMutation.isPending} className="w-full gap-2">
              <ScanSearch className="h-4 w-4" />
              {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze Resume'}
            </Button>
          </Card>

          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">How it works</h2>
            <ol className="list-decimal space-y-3 pl-5 text-sm text-slate-600 dark:text-slate-400">
              <li>Upload and select your master resume</li>
              <li>Paste the target job description</li>
              <li>Get ATS score, keyword gaps, and skill analysis</li>
              <li>Review recommendations and tailored resume</li>
              <li>Download optimized PDF or DOCX</li>
            </ol>
            <p className="mt-6 rounded-lg bg-amber-50 p-3 text-xs text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
              We never invent experience, education, certifications, or skills you do not already possess.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
