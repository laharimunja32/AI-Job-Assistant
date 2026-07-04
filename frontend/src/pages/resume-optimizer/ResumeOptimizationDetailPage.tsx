import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Download, Trash2 } from 'lucide-react';
import {
  ATSScoreCard,
  KeywordComparison,
  KeywordMatchPieChart,
  MatchedSkillsCard,
  MissingSkillsCard,
  OverallScoreRadarChart,
  RecommendationPanel,
  ResumePreview,
  SkillMatchBarChart,
} from '@/components/resume-optimizer';
import { useDeleteResumeOptimization, useResumeOptimization } from '@/hooks';
import { resumeOptimizerService } from '@/services';
import { Button, ConfirmDialog, ErrorState } from '@/components/ui';
import { PageLoader } from '@/components/ui/Loader';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';

export default function ResumeOptimizationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const analysisId = Number(id);
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data, isLoading, error, refetch } = useResumeOptimization(analysisId, Boolean(analysisId));
  const deleteMutation = useDeleteResumeOptimization();
  const [showDelete, setShowDelete] = useState(false);
  const [downloading, setDownloading] = useState<'pdf' | 'docx' | null>(null);

  const handleDownload = async (format: 'pdf' | 'docx') => {
    setDownloading(format);
    try {
      const { data: blob } = await resumeOptimizerService.download(analysisId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `optimized_resume_${analysisId}.${format}`;
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
      await deleteMutation.mutateAsync(analysisId);
      addToast('Analysis deleted', 'success');
      navigate('/resume-optimizer/history');
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
          <Link to="/resume-optimizer/history" className="text-slate-500 hover:text-slate-700">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {data.job_title ?? 'Resume Analysis'}
            </h1>
            {data.company_name && <p className="text-sm text-slate-500">{data.company_name}</p>}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleDownload('pdf')} disabled={downloading === 'pdf'} className="gap-2">
            <Download className="h-4 w-4" />
            PDF
          </Button>
          <Button variant="outline" onClick={() => handleDownload('docx')} disabled={downloading === 'docx'} className="gap-2">
            <Download className="h-4 w-4" />
            DOCX
          </Button>
          <Button variant="outline" onClick={() => setShowDelete(true)} className="gap-2 text-rose-600">
            <Trash2 className="h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <ATSScoreCard
        atsScore={data.ats_score}
        overallScore={data.overall_score}
        keywordMatch={data.keyword_match}
        skillMatch={data.skill_match}
        experienceMatch={data.experience_match}
        educationMatch={data.education_match}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <KeywordMatchPieChart matched={data.matched_keywords.length} missing={data.missing_keywords.length} />
        <SkillMatchBarChart matchedSkills={data.matched_skills} missingSkills={data.missing_skills} />
      </div>

      <OverallScoreRadarChart
        atsScore={data.ats_score}
        keywordMatch={data.keyword_match}
        skillMatch={data.skill_match}
        experienceMatch={data.experience_match}
        educationMatch={data.education_match}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <KeywordComparison matchedKeywords={data.matched_keywords} missingKeywords={data.missing_keywords} />
        <RecommendationPanel recommendations={data.recommendations} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <MatchedSkillsCard skills={data.matched_skills} />
        <MissingSkillsCard skills={data.missing_skills} />
      </div>

      {data.tailored_resume && <ResumePreview content={data.tailored_resume} />}

      <ConfirmDialog
        open={showDelete}
        title="Delete analysis?"
        message="This will permanently remove this optimization and its downloads."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onClose={() => setShowDelete(false)}
      />
    </div>
  );
}
