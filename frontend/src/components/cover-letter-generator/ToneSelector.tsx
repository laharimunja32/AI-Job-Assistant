const TONES = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'formal', label: 'Formal' },
  { value: 'confident', label: 'Confident' },
] as const;

interface ToneSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function ToneSelector({ value, onChange }: ToneSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Tone</label>
      <div className="flex flex-wrap gap-2">
        {TONES.map((tone) => (
          <button
            key={tone.value}
            type="button"
            onClick={() => onChange(tone.value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              value === tone.value
                ? 'bg-brand-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700'
            }`}
          >
            {tone.label}
          </button>
        ))}
      </div>
    </div>
  );
}
