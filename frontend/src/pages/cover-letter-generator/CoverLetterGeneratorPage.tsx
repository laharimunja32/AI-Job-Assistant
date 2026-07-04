import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, History } from 'lucide-react';
import { LengthSelector, TemplateSelector, ToneSelector } from '@/components/cover-letter-generator';
import { useGenerateCoverLetter, useResumes } from '@/hooks';
import { Button, Card, EmptyState, ErrorState, Input } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';

export default function CoverLetterGeneratorPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: resumesData, isLoading, error, refetch } = useResumes({ page: 1, size: 50 });
  const generateMutation = useGenerateCoverLetter();

  const [resumeId, setResumeId] = useState<number | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [templateName, setTemplateName] = useState('professional');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');

  const activeResume = resumesData?.items.find((r) => r.is_active) ?? resumesData?.items[0];
  const selectedResumeId = resumeId ?? activeResume?.id ?? null;

  const handleGenerate = async () => {
    if (!selectedResumeId) {
      addToast('Please upload a resume first', 'error');
      return;
    }
    if (!jobTitle.trim()) {
      addToast('Job title is required', 'error');
      return;
    }
    if (!companyName.trim()) {
      addToast('Company name is required', 'error');
      return;
    }
    if (jobDescription.trim().length < 10) {
      addToast('Job description must be at least 10 characters', 'error');
      return;
    }
    try {
      const { data } = await generateMutation.mutateAsync({
        resume_id: selectedResumeId,
        job_description: jobDescription.trim(),
        job_title: jobTitle.trim(),
        company_name: companyName.trim(),
        template_name: templateName,
        tone,
        length,
      });
      addToast('Cover letter generated', 'success');
      navigate(`/cover-letter-generator/${data.id}`);
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Cover Letter Generator</h1>
          <p className="text-sm text-slate-500">
            Generate professional cover letters from your resume and a job description.
          </p>
        </div>
        <Link to="/cover-letter-generator/history">
          <Button variant="outline" className="gap-2">
            <History className="h-4 w-4" />
            View History
          </Button>
        </Link>
      </div>

      {!resumesData?.items.length ? (
        <EmptyState
          title="No resume uploaded"
          description="Upload a master resume before generating a cover letter."
          actionLabel="Go to Resumes"
          onAction={() => navigate('/resumes')}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="space-y-5 p-6">
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

            <h2 className="pt-2 text-lg font-semibold text-slate-900 dark:text-slate-100">2. Job Details</h2>
            <Input placeholder="Job title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
            <Input placeholder="Company name" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />

            <h2 className="pt-2 text-lg font-semibold text-slate-900 dark:text-slate-100">3. Paste Job Description</h2>
            <textarea
              className="min-h-40 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800"
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />

            <TemplateSelector value={templateName} onChange={setTemplateName} />
            <ToneSelector value={tone} onChange={setTone} />
            <LengthSelector value={length} onChange={setLength} />

            <Button onClick={handleGenerate} disabled={generateMutation.isPending} className="w-full gap-2">
              <FileText className="h-4 w-4" />
              {generateMutation.isPending ? 'Generating...' : 'Generate Cover Letter'}
            </Button>
          </Card>

          <Card className="p-6">
            <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">How it works</h2>
            <ol className="list-decimal space-y-3 pl-5 text-sm text-slate-600 dark:text-slate-400">
              <li>Select your resume and enter job details</li>
              <li>Choose a template, tone, and length</li>
              <li>AI generates a tailored cover letter from your real experience</li>
              <li>Edit, preview, and download as PDF or DOCX</li>
            </ol>
            <p className="mt-6 rounded-lg bg-amber-50 p-3 text-xs text-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
              We never invent experience — only resume and profile data is used.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
