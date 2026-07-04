import { Card } from '@/components/ui';
import { Chip } from '@/components/ui/Chip';

interface KeywordComparisonProps {
  matchedKeywords: string[];
  missingKeywords: string[];
}

export function KeywordComparison({ matchedKeywords, missingKeywords }: KeywordComparisonProps) {
  return (
    <Card className="p-4">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-slate-100">Keyword Comparison</h3>
      <div className="space-y-4">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-emerald-600">Matched ({matchedKeywords.length})</p>
          <div className="flex flex-wrap gap-2">
            {matchedKeywords.length > 0 ? (
              matchedKeywords.map((kw) => <Chip key={kw} label={kw} className="bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300" />)
            ) : (
              <p className="text-sm text-slate-500">No matched keywords yet.</p>
            )}
          </div>
        </div>
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-amber-600">Missing ({missingKeywords.length})</p>
          <div className="flex flex-wrap gap-2">
            {missingKeywords.length > 0 ? (
              missingKeywords.map((kw) => <Chip key={kw} label={kw} className="bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300" />)
            ) : (
              <p className="text-sm text-slate-500">All key terms are covered.</p>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
