import { Textarea } from '@/components/ui/Input';

interface CoverLetterEditorProps {
  value: string;
  onChange: (next: string) => void;
}

export function CoverLetterEditor({ value, onChange }: CoverLetterEditorProps) {
  return <Textarea label="Edit cover letter" rows={10} value={value} onChange={(e) => onChange(e.target.value)} />;
}
