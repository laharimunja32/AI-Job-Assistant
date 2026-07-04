import { Card, Textarea } from '@/components/ui';

interface CoverLetterEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function CoverLetterEditor({ value, onChange, disabled }: CoverLetterEditorProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">Edit Cover Letter</h3>
      <Textarea
        className="min-h-80 font-mono text-sm"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Your cover letter content..."
      />
    </Card>
  );
}
