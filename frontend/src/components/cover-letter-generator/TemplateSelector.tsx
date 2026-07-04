const TEMPLATES = [
  { value: 'professional', label: 'Professional', description: 'Classic business format with clear sections' },
  { value: 'modern', label: 'Modern', description: 'Clean headings with structured sections' },
  { value: 'simple', label: 'Simple', description: 'Minimal formatting, direct paragraphs' },
] as const;

interface TemplateSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export function TemplateSelector({ value, onChange }: TemplateSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Template</label>
      <div className="grid gap-2 sm:grid-cols-3">
        {TEMPLATES.map((template) => (
          <button
            key={template.value}
            type="button"
            onClick={() => onChange(template.value)}
            className={`rounded-lg border p-3 text-left transition-colors ${
              value === template.value
                ? 'border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-900/30'
                : 'border-slate-200 hover:border-brand-300 dark:border-slate-700 dark:hover:border-brand-700'
            }`}
          >
            <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{template.label}</p>
            <p className="mt-1 text-xs text-slate-500">{template.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
