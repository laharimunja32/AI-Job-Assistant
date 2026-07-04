import { Card } from '@/components/ui';

interface ResumePreviewProps {
  content: string;
  title?: string;
}

export function ResumePreview({ content, title = 'Tailored Resume Preview' }: ResumePreviewProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      <div className="max-h-[32rem] overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-800 dark:text-slate-200">{content}</pre>
      </div>
    </Card>
  );
}
