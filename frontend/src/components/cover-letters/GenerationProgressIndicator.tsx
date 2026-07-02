interface GenerationProgressIndicatorProps {
  status: string | null;
}

export function GenerationProgressIndicator({ status }: GenerationProgressIndicatorProps) {
  const width = status === 'completed' ? '100%' : status === 'processing' ? '65%' : status === 'failed' ? '100%' : '30%';
  const label =
    status === 'queued'
      ? 'Queued'
      : status === 'processing'
        ? 'Generating company-specific content'
        : status === 'completed'
          ? 'Completed'
          : status === 'failed'
            ? 'Failed'
            : 'Preparing';

  return (
    <div className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
      <p className="text-sm font-medium">Generation progress</p>
      <div className="mt-2 h-2 w-full overflow-hidden rounded bg-slate-200 dark:bg-slate-700">
        <div className="h-2 rounded bg-brand-600 transition-all" style={{ width }} />
      </div>
      <p className="mt-2 text-xs text-slate-500">{label}</p>
    </div>
  );
}
