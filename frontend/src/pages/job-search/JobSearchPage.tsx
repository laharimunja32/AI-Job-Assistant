import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJobSearchMutation, useSaveJob } from '@/hooks';
import {
  JobCard,
  JobSearchFilters,
  JobDetailsDrawer,
  CompanyCard,
} from '@/components/job-search';
import { Pagination } from '@/components/ui/Pagination';
import { PageLoader } from '@/components/ui/Loader';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';
import type { LiveJobSearchParams, LiveJobResult } from '@/services/jobSearch.service';

export default function JobSearchPage() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [filters, setFilters] = useState<LiveJobSearchParams>({ keyword: 'python', page: 1, size: 12 });
  const [results, setResults] = useState<LiveJobResult[]>([]);
  const [total, setTotal] = useState(0);
  const [selectedJob, setSelectedJob] = useState<LiveJobResult | null>(null);
  const searchMutation = useJobSearchMutation();
  const saveMutation = useSaveJob();

  const handleSearch = async () => {
    try {
      const { data } = await searchMutation.mutateAsync(filters);
      setResults(data.items);
      setTotal(data.total);
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const handleSave = async (job: LiveJobResult) => {
    try {
      await saveMutation.mutateAsync({
        job_id: job.id ?? undefined,
        job_title: job.title,
        company_name: job.company,
        salary: job.salary,
        location: job.location,
        skills: job.skills,
        employment_type: job.employment_type,
        experience: job.experience,
        job_url: job.job_url,
        company_logo: job.company_logo,
        description_preview: job.description_preview,
      });
      addToast('Job saved', 'success');
    } catch (err) {
      addToast(parseApiError(err), 'error');
    }
  };

  const companies = [...new Map(results.map((j) => [j.company, j])).values()];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Live Job Search</h1>
        <p className="mt-1 text-sm text-slate-500">Search across providers with advanced filters</p>
      </div>

      <JobSearchFilters
        filters={filters}
        onChange={setFilters}
        onSearch={handleSearch}
        loading={searchMutation.isPending}
      />

      {searchMutation.isPending && <PageLoader />}

      {!searchMutation.isPending && results.length === 0 && (
        <EmptyState title="No results yet" description="Run a search to discover live job postings." />
      )}

      {companies.length > 0 && (
        <div className="grid gap-4 md:grid-cols-3">
          {companies.slice(0, 3).map((job) => (
            <CompanyCard key={job.company} name={job.company} logo={job.company_logo} location={job.location} />
          ))}
        </div>
      )}

      {results.length > 0 && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {results.map((job, idx) => (
              <JobCard
                key={`${job.title}-${idx}`}
                job={job}
                onSelect={setSelectedJob}
                onSave={handleSave}
              />
            ))}
          </div>
          <Pagination
            page={filters.page ?? 1}
            total={total}
            size={filters.size ?? 12}
            onPageChange={(page) => {
              const next = { ...filters, page };
              setFilters(next);
              searchMutation.mutateAsync(next).then(({ data }) => {
                setResults(data.items);
                setTotal(data.total);
              });
            }}
          />
        </>
      )}

      <JobDetailsDrawer
        job={selectedJob}
        open={!!selectedJob}
        onClose={() => setSelectedJob(null)}
        onSave={handleSave}
        onStartApplication={(job) =>
          navigate('/browser-application', {
            state: {
              job_id: job.id,
              job_title: job.title,
              company_name: job.company,
              apply_url: job.job_url,
            },
          })
        }
      />
    </div>
  );
}
