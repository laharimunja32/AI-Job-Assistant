const LENGTHS = [
  { value: 'short', label: 'Short', description: '~1 paragraph' },
  { value: 'medium', label: 'Medium', description: 'Balanced' },
  { value: 'long', label: 'Long', description: 'Detailed' },
] as const;

interface LengthSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function LengthSelector({ value, onChange }: LengthSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Length</label>
      <div className="flex flex-wrap gap-2">
        {LENGTHS.map((length) => (
          <button
            key={length.value}
            type="button"
            onClick={() => onChange(length.value)}
            className={`rounded-lg border px-4 py-2 text-sm transition-colors ${
              value === length.value
                ? 'border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-900/30'
                : 'border-slate-200 hover:border-brand-300 dark:border-slate-700'
            }`}
          >
            <span className="font-medium">{length.label}</span>
            <span className="ml-1 text-xs text-slate-500">({length.description})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
