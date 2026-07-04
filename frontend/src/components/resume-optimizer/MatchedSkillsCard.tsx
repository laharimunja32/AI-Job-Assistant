import { Card } from '@/components/ui';
import { Chip } from '@/components/ui/Chip';

interface MatchedSkillsCardProps {
  skills: string[];
}

export function MatchedSkillsCard({ skills }: MatchedSkillsCardProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Matched Skills</h3>
      {skills.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <Chip key={skill} label={skill} className="bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300" />
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No skills matched yet. Review the job description and your profile.</p>
      )}
    </Card>
  );
}
