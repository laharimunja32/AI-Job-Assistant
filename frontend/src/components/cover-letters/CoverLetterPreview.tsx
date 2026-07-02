import { Card } from '@/components/ui/Card';

export function CoverLetterPreview({ content }: { content: string | null | undefined }) {
  return (
    <Card>
      <p className="mb-2 text-sm font-medium">Preview</p>
      <div className="max-h-64 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs dark:border-slate-700 dark:bg-slate-900">
        <pre className="whitespace-pre-wrap">{content ?? 'No preview available.'}</pre>
      </div>
    </Card>
  );
}
