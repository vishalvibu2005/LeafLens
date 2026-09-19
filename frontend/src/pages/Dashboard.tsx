import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sprout } from 'lucide-react';
import { PageShell } from '../components/layout/PageShell';
import { GlassCard, GlassButton } from '../components/glass/Glass';
import { LeafLensMark } from '../components/common/LeafLensMark';
import { api } from '../services/api';
import type { DashboardStats } from '../types/analysis';

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    api.dashboardStats().then(setStats).catch(() => setStats({ has_data: false }));
  }, []);

  return (
    <PageShell>
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center gap-8 py-10 text-center md:py-16"
      >
        <div className="glass-soft flex h-24 w-24 items-center justify-center rounded-full">
          <LeafLensMark size={56} />
        </div>
        <div>
          <h1 className="font-display text-4xl leading-tight md:text-6xl">
            See Your Leaf Through a<br />Smarter Lens.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-[var(--ink-soft)] md:text-lg">
            AI-powered plant leaf detection, species classification, health assessment and visible growth-stage analysis using computer vision.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-3">
          <Link to="/analyze">
            <GlassButton>Analyze a Leaf</GlassButton>
          </Link>
        </div>
      </motion.section>

      <section className="mt-8">
        {stats?.has_data ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard label="Total Analyses" value={String(stats.total_analyses)} />
            <StatCard label="Leaves Detected" value={String(stats.leaves_detected)} />
            <StatCard label="Most Analyzed Type" value={stats.most_analyzed_type ?? '—'} />
            <StatCard
              label="Average Model Confidence"
              value={stats.average_confidence != null ? `${Math.round(stats.average_confidence * 100)}%` : '—'}
            />
            <StatCard label="Healthy Leaves" value={String(stats.healthy_leaves ?? 0)} />
            <StatCard label="Affected Leaves" value={String(stats.affected_leaves ?? 0)} />
          </div>
        ) : (
          <GlassCard className="flex flex-col items-center gap-3 px-6 py-12 text-center">
            <Sprout size={30} style={{ color: 'var(--accent)' }} />
            <p className="font-display text-xl">No analyses yet</p>
            <p className="max-w-sm text-sm text-[var(--ink-soft)]">
              Analyze your first leaf to start building your analysis history and dashboard statistics.
            </p>
            <Link to="/analyze" className="mt-2">
              <GlassButton>Analyze a Leaf</GlassButton>
            </Link>
          </GlassCard>
        )}
      </section>
    </PageShell>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <GlassCard className="p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--ink-soft)]">{label}</p>
      <p className="mt-2 font-display text-3xl">{value}</p>
    </GlassCard>
  );
}
