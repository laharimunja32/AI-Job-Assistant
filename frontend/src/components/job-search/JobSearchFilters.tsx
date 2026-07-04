import { Input, Select } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import type { LiveJobSearchParams } from '@/services/jobSearch.service';

interface JobSearchFiltersProps {
  filters: LiveJobSearchParams;
  onChange: (filters: LiveJobSearchParams) => void;
  onSearch: () => void;
  loading?: boolean;
}

export function JobSearchFilters({ filters, onChange, onSearch, loading }: JobSearchFiltersProps) {
  const set = (key: keyof LiveJobSearchParams, value: string | boolean | undefined) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <Card>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Input
          label="Keyword"
          placeholder="e.g. Python, React"
          value={filters.keyword ?? ''}
          onChange={(e) => set('keyword', e.target.value || undefined)}
        />
        <Input
          label="Location"
          placeholder="City or region"
          value={filters.location ?? ''}
          onChange={(e) => set('location', e.target.value || undefined)}
        />
        <Input
          label="Company"
          placeholder="Company name"
          value={filters.company ?? ''}
          onChange={(e) => set('company', e.target.value || undefined)}
        />
        <Input
          label="Salary"
          placeholder="e.g. 12-18 LPA"
          value={filters.salary ?? ''}
          onChange={(e) => set('salary', e.target.value || undefined)}
        />
        <Input
          label="Experience"
          placeholder="e.g. 0-2 years"
          value={filters.experience ?? ''}
          onChange={(e) => set('experience', e.target.value || undefined)}
        />
        <Select
          label="Employment Type"
          value={filters.employment_type ?? ''}
          onChange={(e) => set('employment_type', e.target.value || undefined)}
          options={[
            { value: '', label: 'Any' },
            { value: 'Full Time', label: 'Full Time' },
            { value: 'Part Time', label: 'Part Time' },
            { value: 'Contract', label: 'Contract' },
            { value: 'Internship', label: 'Internship' },
          ]}
        />
        <Select
          label="Date Posted"
          value={filters.date_posted ?? ''}
          onChange={(e) => set('date_posted', e.target.value || undefined)}
          options={[
            { value: '', label: 'Any time' },
            { value: 'today', label: 'Today' },
            { value: 'week', label: 'This week' },
            { value: 'month', label: 'This month' },
          ]}
        />
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Work Mode</span>
          <div className="flex flex-wrap gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!filters.remote}
                onChange={(e) => onChange({ ...filters, remote: e.target.checked || undefined, hybrid: false, onsite: false })}
              />
              Remote
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!filters.hybrid}
                onChange={(e) => onChange({ ...filters, hybrid: e.target.checked || undefined, remote: false, onsite: false })}
              />
              Hybrid
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!filters.onsite}
                onChange={(e) => onChange({ ...filters, onsite: e.target.checked || undefined, remote: false, hybrid: false })}
              />
              On-site
            </label>
          </div>
        </div>
      </div>
      <div className="mt-4">
        <Button onClick={onSearch} loading={loading}>
          Search Jobs
        </Button>
      </div>
    </Card>
  );
}
