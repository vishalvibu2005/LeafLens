import { useEffect, useState } from 'react';
import { useLocation, useParams, Link } from 'react-router-dom';
import { PageShell } from '../components/layout/PageShell';
import { GlassBadge, GlassButton } from '../components/glass/Glass';
import { ImageViewer } from '../components/results/ImageViewer';
import { LeafSelector } from '../components/results/LeafSelector';
import { LeafTypeCard, GrowthStageCard, HealthCard } from '../components/results/PredictionCards';
import { FeatureDashboard } from '../components/results/FeatureDashboard';
import { EmptyState } from '../components/common/EmptyState';
import { api } from '../services/api';
import type { Analysis } from '../types/analysis';

export function Results() {
  const { id } = useParams();
  const location = useLocation();
  const [analysis, setAnalysis] = useState<Analysis | null>((location.state as Analysis) ?? null);
  const [activeLeafId, setActiveLeafId] = useState<number | null>(null);
  const [loading, setLoading] = useState(!location.state);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (analysis) {
      setActiveLeafId(analysis.leaf_results[0]?.leaf_id ?? null);
      return;
    }
    if (!id) return;
    setLoading(true);
    api
      .historyItem(id)
      .then((a) => {
        setAnalysis(a);
        setActiveLeafId(a.leaf_results[0]?.leaf_id ?? null);
      })
      .catch(() => setError('This analysis could not be found.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <PageShell>
        <p className="text-center text-[var(--ink-soft)]">Loading analysis…</p>
      </PageShell>
    );
  }

  if (error || !analysis) {
    return (
      <PageShell>
        <EmptyState
          title="Analysis not found"
          subtitle={error ?? 'This analysis may have been deleted.'}
          action={
            <Link to="/analyze">
              <GlassButton>Analyze a Leaf</GlassButton>
            </Link>
          }
        />
      </PageShell>
    );
  }

  const activeLeaf = analysis.leaf_results.find((l) => l.leaf_id === activeLeafId) ?? null;

  return (
    <PageShell>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-[var(--ink-soft)]">Analysis Complete</p>
          <div className="mt-1 flex flex-wrap items-baseline gap-3">
            <h1 className="font-display text-3xl">
              {activeLeaf?.type.label ?? (activeLeaf?.type.is_demo ? 'Demo Mode' : 'Unknown')}
            </h1>
            {activeLeaf?.growth_stage.label && (
              <span className="font-display text-xl text-[var(--ink-soft)]">
                · {activeLeaf.growth_stage.label}
              </span>
            )}
          </div>
        </div>
        {analysis.mode === 'demo' && <GlassBadge tone="demo">Running in Demo Mode</GlassBadge>}
      </div>

      <div className="mb-6">
        <LeafSelector
          leaves={analysis.leaf_results}
          activeId={activeLeafId ?? 0}
          onSelect={setActiveLeafId}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <ImageViewer analysis={analysis} activeLeaf={activeLeaf} />
        <div className="flex flex-col gap-5">
          {activeLeaf && <LeafTypeCard leaf={activeLeaf} />}
          {activeLeaf && <HealthCard leaf={activeLeaf} />}
          {activeLeaf && <GrowthStageCard leaf={activeLeaf} />}
        </div>
      </div>

      {activeLeaf && (
        <div className="mt-8">
          <h2 className="mb-4 font-display text-xl">Leaf Measurements</h2>
          <FeatureDashboard leaf={activeLeaf} />
        </div>
      )}
    </PageShell>
  );
}
