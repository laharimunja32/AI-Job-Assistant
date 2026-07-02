import type { InterviewSessionProgress } from '@/types';

interface InterviewProgressProps {
  progress: InterviewSessionProgress;
  elapsedSeconds?: number;
}

export function InterviewProgress({ progress, elapsedSeconds }: InterviewProgressProps) {
  const minutes = elapsedSeconds != null ? Math.floor(elapsedSeconds / 60) : 0;
  const seconds = elapsedSeconds != null ? elapsedSeconds % 60 : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-300">
        <span>
          Progress: {progress.questions_answered} / {progress.total_questions}
        </span>
        {elapsedSeconds != null && (
          <span>
            Timer: {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </span>
        )}
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div
          className="h-full rounded-full bg-brand-600 transition-all"
          style={{ width: `${progress.percent_complete}%` }}
        />
      </div>
    </div>
  );
}
