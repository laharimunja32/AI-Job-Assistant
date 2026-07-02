import { useMemo, useState } from 'react';
import { useProcessRecruitmentEmail, useRecruitmentEmails } from '@/hooks';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Pagination } from '@/components/ui/Pagination';
import { parseApiError, formatDateTime } from '@/utils';

export default function RecruitmentEmailsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<'desc' | 'asc'>('desc');
  const [provider, setProvider] = useState('gmail');
  const [sender, setSender] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');

  const { data, isLoading, error } = useRecruitmentEmails(page, 10);
  const processMutation = useProcessRecruitmentEmail();

  const filtered = useMemo(() => {
    const items = (data?.items ?? []).filter((item) =>
      `${item.subject} ${item.sender} ${item.company_name ?? ''}`.toLowerCase().includes(search.toLowerCase()),
    );
    return [...items].sort((a, b) =>
      sort === 'desc'
        ? +new Date(b.received_time) - +new Date(a.received_time)
        : +new Date(a.received_time) - +new Date(b.received_time),
    );
  }, [data?.items, search, sort]);

  const submit = async () => {
    await processMutation.mutateAsync({
      provider,
      authorization_confirmed: true,
      sender,
      subject,
      body,
      received_time: new Date().toISOString(),
    });
    setSender('');
    setSubject('');
    setBody('');
  };

  if (isLoading) return <p>Loading recruitment emails...</p>;
  if (error) return <p className="text-red-500">{parseApiError(error)}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Recruitment Emails</h1>
        <p className="mt-1 text-sm text-slate-500">Official integration only. No mailbox scraping or password storage.</p>
      </div>

      <Card className="space-y-3">
        <p className="text-sm font-medium">Process authorized provider email</p>
        <div className="grid gap-3 md:grid-cols-2">
          <Select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            options={[{ value: 'gmail', label: 'Gmail API' }, { value: 'outlook', label: 'Microsoft Graph' }]}
          />
          <Input placeholder="Sender" value={sender} onChange={(e) => setSender(e.target.value)} />
          <Input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} className="md:col-span-2" />
          <Textarea label="Body" value={body} onChange={(e) => setBody(e.target.value)} rows={4} className="md:col-span-2" />
        </div>
        <Button onClick={submit} loading={processMutation.isPending} disabled={!sender || !subject}>
          Process Email
        </Button>
      </Card>

      <div className="grid gap-3 md:grid-cols-2">
        <Input placeholder="Search sender/company/subject" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Select
          value={sort}
          onChange={(e) => setSort(e.target.value as 'desc' | 'asc')}
          options={[{ value: 'desc', label: 'Newest first' }, { value: 'asc', label: 'Oldest first' }]}
        />
      </div>

      <div className="space-y-3">
        {filtered.map((item) => (
          <Card key={item.id} className="space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="font-semibold">{item.subject}</p>
                <p className="text-sm text-slate-500">{item.sender} ┬╖ {item.company_name ?? 'Unknown company'}</p>
              </div>
              <Badge variant={item.offer ? 'success' : item.rejection ? 'danger' : item.online_assessment ? 'warning' : 'info'}>
                {item.event_type}
              </Badge>
            </div>
            <p className="text-xs text-slate-500">
              Received: {formatDateTime(item.received_time)} ┬╖ Deadline: {item.deadline ? formatDateTime(item.deadline) : 'ΓÇö'}
            </p>
          </Card>
        ))}
        {filtered.length === 0 && <Card><p className="text-sm text-slate-500">No recruitment emails found.</p></Card>}
      </div>
      {data && <Pagination page={data.page} size={data.size} total={data.total} onPageChange={setPage} />}
    </div>
  );
}
