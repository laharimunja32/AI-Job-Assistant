import { Card } from '@/components/ui';
import { Chip } from '@/components/ui/Chip';

interface MissingSkillsCardProps {
  skills: string[];
}

export function MissingSkillsCard({ skills }: MissingSkillsCardProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Missing Skills</h3>
      {skills.length > 0 ? (
        <>
          <p className="mb-3 text-xs text-slate-500">Only highlight skills you genuinely possess — never invent experience.</p>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill) => (
              <Chip key={skill} label={skill} className="bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" />
            ))}
          </div>
        </>
      ) : (
        <p className="text-sm text-slate-500">Your resume covers all detected role skills.</p>
      )}
    </Card>
  );
}
