import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Trash } from 'lucide-react';
import { PageShell } from '../components/layout/PageShell';
import { HistoryCard } from '../components/history/HistoryCard';
import { EmptyState } from '../components/common/EmptyState';
import { GlassButton, GlassTabs } from '../components/glass/Glass';
import { api } from '../services/api';
import type { Analysis } from '../types/analysis';

export function History() {
  const [items, setItems] = useState<Analysis[]>([]);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<'newest' | 'oldest'>('newest');
  const [loading, setLoading] = useState(true);
  const [confirmClear, setConfirmClear] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .history({ search: search || undefined, sort })
      .then(setItems)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sort]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load();
  };

  const handleDelete = async (analysisId: string) => {
    await api.deleteHistoryItem(analysisId);
    setItems((prev) => prev.filter((a) => a.analysis_id !== analysisId));
  };

  const handleClearAll = async () => {
    if (!confirmClear) {
      setConfirmClear(true);
      return;
    }
    await api.deleteAllHistory();
    setItems([]);
    setConfirmClear(false);
  };

  return (
    <PageShell>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display text-3xl">History</h1>
        {items.length > 0 && (
          <GlassButton variant={confirmClear ? 'danger' : 'ghost'} onClick={handleClearAll}>
            <Trash size={15} />
            {confirmClear ? 'Confirm clear all?' : 'Clear All'}
          </GlassButton>
        )}
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <form onSubmit={handleSearch} className="glass-soft flex flex-1 items-center gap-2 rounded-full px-4 py-2 min-w-[200px]">
          <Search size={15} className="text-[var(--ink-soft)]" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by leaf type…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-[var(--ink-soft)]"
          />
        </form>
        <GlassTabs
          tabs={[
            { id: 'newest', label: 'Newest' },
            { id: 'oldest', label: 'Oldest' },
          ]}
          active={sort}
          onChange={(v) => setSort(v as 'newest' | 'oldest')}
        />
      </div>

      {loading ? (
        <p className="text-center text-[var(--ink-soft)]">Loading history…</p>
      ) : items.length === 0 ? (
        <EmptyState
          title="No analyses yet"
          subtitle="Analyses you run will appear here, with search, filters, and full details."
          action={
            <Link to="/analyze">
              <GlassButton>Analyze a Leaf</GlassButton>
            </Link>
          }
        />
      ) : (
        <div className="flex flex-col gap-3">
          {items.map((a) => (
            <HistoryCard key={a.analysis_id} analysis={a} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </PageShell>
  );
}
