import { Link } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import type { Analysis } from '../../types/analysis';
import { GlassCard, GlassBadge } from '../glass/Glass';

export function HistoryCard({ analysis, onDelete }: { analysis: Analysis; onDelete: (id: string) => void }) {
  const primary = analysis.leaf_results[0];
  return (
    <GlassCard className="flex items-center gap-4 p-4">
      <img
        src={analysis.thumbnail_url}
        alt="Analysis thumbnail"
        className="h-16 w-16 shrink-0 rounded-xl object-cover"
      />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="font-medium">
            {primary?.type.label ?? (primary?.type.is_demo ? 'Demo Mode' : 'Unknown')}
          </p>
          {primary?.growth_stage.label && <GlassBadge>{primary.growth_stage.label}</GlassBadge>}
          {primary?.health.label && (
            <GlassBadge tone={primary.health.label.toLowerCase() === 'healthy' ? 'high' : 'low'}>
              {primary.health.label.toLowerCase() === 'healthy' ? 'Healthy' : 'Affected'}
            </GlassBadge>
          )}
          {analysis.mode === 'demo' && <GlassBadge tone="demo">Demo</GlassBadge>}
        </div>
        <p className="mt-1 text-xs text-[var(--ink-soft)]">
          {analysis.leaf_count} leaf{analysis.leaf_count !== 1 ? 's' : ''} ·{' '}
          {new Date(analysis.created_at).toLocaleString()}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Link
          to={`/history/${analysis.analysis_id}`}
          className="glass-soft rounded-full px-4 py-1.5 text-sm font-medium focus-ring hover:bg-[var(--surface)]"
        >
          View
        </Link>
        <button
          aria-label="Delete analysis"
          onClick={() => onDelete(analysis.analysis_id)}
          className="rounded-full p-2 text-[var(--ink-soft)] hover:text-red-500 focus-ring"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </GlassCard>
  );
}
