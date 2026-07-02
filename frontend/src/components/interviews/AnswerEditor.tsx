import { useState } from 'react';
import { Button, Card } from '@/components/ui';

interface AnswerEditorProps {
  value?: string;
  onSubmit: (answer: string, timeSpentSeconds: number) => void;
  loading?: boolean;
  disabled?: boolean;
}

export function AnswerEditor({ value = '', onSubmit, loading, disabled }: AnswerEditorProps) {
  const [answer, setAnswer] = useState(value);
  const [startedAt] = useState(Date.now());

  return (
    <Card className="p-4">
      <label className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">Your answer</label>
      <textarea
        className="min-h-[160px] w-full rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-900 outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Structure your answer with context, actions, and measurable results..."
        disabled={disabled || loading}
      />
      <div className="mt-3 flex justify-end">
        <Button
          loading={loading}
          disabled={disabled || !answer.trim()}
          onClick={() => onSubmit(answer.trim(), Math.round((Date.now() - startedAt) / 1000))}
        >
          Save & Continue
        </Button>
      </div>
    </Card>
  );
}
