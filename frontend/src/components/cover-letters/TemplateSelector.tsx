import type { CoverLetterTemplate } from '@/types';
import { Select } from '@/components/ui/Input';

interface TemplateSelectorProps {
  templates: CoverLetterTemplate[];
  selectedTemplateId: number | null;
  onSelect: (templateId: number | null) => void;
}

export function TemplateSelector({ templates, selectedTemplateId, onSelect }: TemplateSelectorProps) {
  return (
    <Select
      label="Template"
      value={selectedTemplateId ? String(selectedTemplateId) : 'none'}
      onChange={(e) => onSelect(e.target.value === 'none' ? null : Number(e.target.value))}
      options={[
        { value: 'none', label: 'No template preference' },
        ...templates.map((item) => ({ value: String(item.id), label: `${item.name}${item.is_default ? ' (default)' : ''}` })),
      ]}
    />
  );
}
