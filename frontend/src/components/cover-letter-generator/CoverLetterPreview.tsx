import { Card } from '@/components/ui';

interface CoverLetterPreviewProps {
  content: string;
}

export function CoverLetterPreview({ content }: CoverLetterPreviewProps) {
  return (
    <Card className="p-6">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Preview</h3>
      <div className="max-h-[32rem] overflow-y-auto whitespace-pre-wrap rounded-lg border border-slate-200 bg-white p-4 text-sm leading-relaxed text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
        {content || 'No content to preview.'}
      </div>
    </Card>
  );
}
