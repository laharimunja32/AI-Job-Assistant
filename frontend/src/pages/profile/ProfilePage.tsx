import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2 } from 'lucide-react';
import { useProfile, profileKeys } from '@/hooks/useProfile';
import { profileService } from '@/services';
import { PageLoader } from '@/components/ui/Loader';
import { ErrorState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input, Textarea } from '@/components/ui/Input';
import { Chip } from '@/components/ui/Chip';
import { useToast } from '@/contexts/ToastContext';
import { parseApiError } from '@/utils';
import type { Profile } from '@/types';

export default function ProfilePage() {
  const { data: profile, isLoading, error, refetch } = useProfile();
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [skillInput, setSkillInput] = useState('');
  const [roleInput, setRoleInput] = useState('');
  const [locationInput, setLocationInput] = useState('');

  const { register, handleSubmit, control, watch, setValue } = useForm<Profile>({
    values: profile,
  });

  const education = useFieldArray({ control, name: 'education' });
  const certifications = useFieldArray({ control, name: 'certifications' });
  const projects = useFieldArray({ control, name: 'projects' });

  const skills = watch('skills') ?? [];
  const roles = watch('preferred_job_roles') ?? [];
  const locations = watch('preferred_locations') ?? [];

  const mutation = useMutation({
    mutationFn: (data: Partial<Profile>) => profileService.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: profileKeys.all });
      addToast('Profile updated', 'success');
    },
    onError: (err) => addToast(parseApiError(err), 'error'),
  });

  const addToList = (field: 'skills' | 'preferred_job_roles' | 'preferred_locations', value: string, clear: () => void) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    const current = watch(field) ?? [];
    if (!current.includes(trimmed)) setValue(field, [...current, trimmed]);
    clear();
  };

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorState message={parseApiError(error)} onRetry={() => refetch()} />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Profile</h1>
        <p className="mt-1 text-sm text-slate-500">Keep your profile updated for better AI matches</p>
      </div>

      <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-6">
        <Card>
          <h2 className="mb-4 text-lg font-semibold">Personal Information</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="Full name" {...register('full_name')} />
            <Input label="Email" value={profile?.email ?? ''} disabled />
            <Input label="Phone" {...register('phone')} />
            <Input label="Location" {...register('location')} />
            <Input label="Address" className="sm:col-span-2" {...register('address')} />
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold">Skills</h2>
          <div className="mb-3 flex flex-wrap gap-2">
            {skills.map((s) => (
              <Chip key={s} label={s} onRemove={() => setValue('skills', skills.filter((x) => x !== s))} />
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="Add a skill"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addToList('skills', skillInput, () => setSkillInput('')))}
            />
            <Button type="button" variant="outline" onClick={() => addToList('skills', skillInput, () => setSkillInput(''))}>
              Add
            </Button>
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Education</h2>
            <Button type="button" size="sm" variant="outline" onClick={() => education.append({ institution: '', degree: '', field: '', start_date: '', end_date: '', description: '' })}>
              <Plus className="h-4 w-4" /> Add
            </Button>
          </div>
          {education.fields.map((field, i) => (
            <div key={field.id} className="mb-4 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
              <div className="mb-2 flex justify-end">
                <button type="button" onClick={() => education.remove(i)} className="text-red-500"><Trash2 className="h-4 w-4" /></button>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <Input label="Institution" {...register(`education.${i}.institution`)} />
                <Input label="Degree" {...register(`education.${i}.degree`)} />
                <Input label="Field" {...register(`education.${i}.field`)} />
                <Input label="Start" {...register(`education.${i}.start_date`)} />
                <Input label="End" {...register(`education.${i}.end_date`)} />
              </div>
            </div>
          ))}
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Certifications</h2>
            <Button type="button" size="sm" variant="outline" onClick={() => certifications.append({ name: '', issuer: '', issued_date: '', expires_at: '' })}>
              <Plus className="h-4 w-4" /> Add
            </Button>
          </div>
          {certifications.fields.map((field, i) => (
            <div key={field.id} className="mb-4 grid gap-3 rounded-lg border border-slate-200 p-4 sm:grid-cols-2 dark:border-slate-700">
              <Input label="Name" {...register(`certifications.${i}.name`)} />
              <Input label="Issuer" {...register(`certifications.${i}.issuer`)} />
              <Input label="Issued" {...register(`certifications.${i}.issued_date`)} />
              <Input label="Expires" {...register(`certifications.${i}.expires_at`)} />
            </div>
          ))}
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Projects</h2>
            <Button type="button" size="sm" variant="outline" onClick={() => projects.append({ name: '', description: '', url: '' })}>
              <Plus className="h-4 w-4" /> Add
            </Button>
          </div>
          {projects.fields.map((field, i) => (
            <div key={field.id} className="mb-4 space-y-3 rounded-lg border border-slate-200 p-4 dark:border-slate-700">
              <Input label="Name" {...register(`projects.${i}.name`)} />
              <Textarea label="Description" {...register(`projects.${i}.description`)} />
              <Input label="URL" {...register(`projects.${i}.url`)} />
            </div>
          ))}
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold">Preferences</h2>
          <div className="mb-4">
            <p className="mb-2 text-sm font-medium">Preferred roles</p>
            <div className="mb-2 flex flex-wrap gap-2">
              {roles.map((r) => (
                <Chip key={r} label={r} onRemove={() => setValue('preferred_job_roles', roles.filter((x) => x !== r))} />
              ))}
            </div>
            <div className="flex gap-2">
              <Input value={roleInput} onChange={(e) => setRoleInput(e.target.value)} placeholder="e.g. Software Engineer" />
              <Button type="button" variant="outline" onClick={() => addToList('preferred_job_roles', roleInput, () => setRoleInput(''))}>Add</Button>
            </div>
          </div>
          <div className="mb-4">
            <p className="mb-2 text-sm font-medium">Preferred locations</p>
            <div className="mb-2 flex flex-wrap gap-2">
              {locations.map((l) => (
                <Chip key={l} label={l} onRemove={() => setValue('preferred_locations', locations.filter((x) => x !== l))} />
              ))}
            </div>
            <div className="flex gap-2">
              <Input value={locationInput} onChange={(e) => setLocationInput(e.target.value)} placeholder="e.g. Bangalore" />
              <Button type="button" variant="outline" onClick={() => addToList('preferred_locations', locationInput, () => setLocationInput(''))}>Add</Button>
            </div>
          </div>
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" {...register('work_preferences.remote')} className="rounded" />
              Open to remote
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" {...register('work_preferences.relocation')} className="rounded" />
              Open to relocation
            </label>
          </div>
          <Input label="Availability" className="mt-4" {...register('work_preferences.availability')} />
        </Card>

        <Card>
          <h2 className="mb-4 text-lg font-semibold">Social Links</h2>
          <div className="grid gap-4">
            <Input label="LinkedIn" {...register('linkedin_url')} />
            <Input label="GitHub" {...register('github_url')} />
            <Input label="Portfolio" {...register('portfolio_url')} />
          </div>
        </Card>

        <Button type="submit" loading={mutation.isPending} className="w-full sm:w-auto">
          Save profile
        </Button>
      </form>
    </div>
  );
}
