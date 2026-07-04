import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { cn } from '@/utils';

const STEPS = ['Started', 'Navigate', 'Autofill', 'Upload', 'Review', 'Submit'] as const;

interface ApplicationProgressProps {
  currentStep: number;
  status?: string;
}

export function ApplicationProgress({ currentStep, status }: ApplicationProgressProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        {STEPS.map((step, index) => {
          const done = index < currentStep;
          const active = index === currentStep;
          return (
            <div key={step} className="flex flex-1 flex-col items-center">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2',
                  done && 'border-emerald-500 bg-emerald-50 text-emerald-600',
                  active && 'border-brand-500 bg-brand-50 text-brand-600',
                  !done && !active && 'border-slate-200 text-slate-400',
                )}
              >
                {done ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Circle className="h-4 w-4" />
                )}
              </div>
              <span className="mt-1 text-xs text-slate-500">{step}</span>
            </div>
          );
        })}
      </div>
      {status && <p className="text-center text-sm capitalize text-slate-600">Status: {status.replace(/_/g, ' ')}</p>}
    </div>
  );
}
