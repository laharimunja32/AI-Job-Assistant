import { Card } from '@/components/ui';

interface ResumeDiffViewerProps {
  original: string;
  tailored: string;
}

export function ResumeDiffViewer({ original, tailored }: ResumeDiffViewerProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Original Resume</h3>
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap text-xs text-slate-700 dark:text-slate-300">{original}</pre>
      </Card>
      <Card className="p-4">
        <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Tailored Resume</h3>
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap text-xs text-slate-700 dark:text-slate-300">{tailored}</pre>
      </Card>
    </div>
  );
}
