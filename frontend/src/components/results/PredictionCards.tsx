import type { LeafResult } from '../../types/analysis';
import { GlassCard, GlassBadge } from '../glass/Glass';
import { ConfidenceBar } from '../charts/ConfidenceBar';
import { ConfidenceNote } from '../common/ConfidenceNote';

const STAGES = ['Early', 'Mature'];

function bandTone(band: string | null) {
  if (band === 'HIGH') return 'high';
  if (band === 'MEDIUM') return 'medium';
  if (band === 'LOW') return 'low';
  return 'default';
}

export function LeafTypeCard({ leaf }: { leaf: LeafResult }) {
  const { type } = leaf;

  if (type.is_demo) {
    return (
      <GlassCard className="p-6">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Leaf Type</p>
        <GlassBadge tone="demo">Demo Mode</GlassBadge>
        <p className="mt-3 text-sm text-[var(--ink-soft)]">
          The leaf-type classification model is not currently installed. Train and install a model to enable
          real species predictions.
        </p>
      </GlassCard>
    );
  }

  if (!type.label || (type.confidence ?? 0) < 0.55) {
    return (
      <GlassCard className="p-6">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Leaf Type</p>
        <p className="font-display text-xl">Unknown / Uncertain</p>
        <p className="mt-2 text-sm text-[var(--ink-soft)]">
          LeafLens could not confidently identify this leaf among the currently supported classes.
          {type.label && ` Possible match: ${type.label} (${Math.round((type.confidence ?? 0) * 100)}%).`}
        </p>
        <p className="mt-2 text-sm text-[var(--ink-soft)]">Try a clearer image or a different leaf.</p>
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Leaf Type</p>
      <div className="flex items-baseline gap-3">
        <p className="font-display text-2xl">{type.label}</p>
        <GlassBadge tone={bandTone(type.band)}>{Math.round((type.confidence ?? 0) * 100)}%</GlassBadge>
      </div>
      <p className="mb-3 mt-1 text-sm text-[var(--ink-soft)]">
        {type.band === 'HIGH' ? 'High confidence' : type.band === 'MEDIUM' ? 'Medium confidence' : 'Low confidence'}
      </p>
      {type.top3.length > 0 && (
        <div className="mt-4 flex flex-col gap-2">
          {type.top3.map((t) => (
            <ConfidenceBar key={t.label} label={t.label} value={t.confidence} />
          ))}
        </div>
      )}
      <div className="mt-4">
        <ConfidenceNote />
      </div>
    </GlassCard>
  );
}

export function GrowthStageCard({ leaf }: { leaf: LeafResult }) {
  const { growth_stage } = leaf;

  if (growth_stage.is_demo) {
    return (
      <GlassCard className="p-6">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">
          Visible Growth Stage
        </p>
        <GlassBadge tone="demo">Demo Mode</GlassBadge>
        <p className="mt-3 text-sm text-[var(--ink-soft)]">
          The growth-stage model is not currently installed. Train and install a model to enable real predictions.
        </p>
      </GlassCard>
    );
  }

  return (
    <GlassCard className="p-6">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">
        Visible Growth Stage
      </p>
      <div className="flex items-baseline gap-3">
        <p className="font-display text-2xl">{growth_stage.label}</p>
        <GlassBadge tone={bandTone(growth_stage.band)}>
          {Math.round((growth_stage.confidence ?? 0) * 100)}%
        </GlassBadge>
      </div>
      <p className="mb-4 mt-1 text-sm text-[var(--ink-soft)]">Model-based visual estimate</p>
      <div className="flex items-center gap-1 text-xs">
        {STAGES.map((s, i) => (
          <div key={s} className="flex flex-1 items-center">
            <div
              className={`flex-1 rounded-full py-1.5 text-center font-medium ${
                s === growth_stage.label ? 'text-white' : 'text-[var(--ink-soft)]'
              }`}
              style={{ backgroundColor: s === growth_stage.label ? 'var(--accent)' : 'var(--surface-2)' }}
            >
              {s}
            </div>
            {i < STAGES.length - 1 && <span className="mx-1 text-[var(--ink-soft)]">→</span>}
          </div>
        ))}
      </div>
    </GlassCard>
  );
}

export function HealthCard({ leaf }: { leaf: LeafResult }) {
  const { health } = leaf;

  if (health.is_demo) {
    return (
      <GlassCard className="p-6">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Leaf Health</p>
        <GlassBadge tone="demo">Model unavailable</GlassBadge>
        <p className="mt-3 text-sm text-[var(--ink-soft)]">
          The health classifier is not currently installed, so LeafLens has not made a health prediction.
        </p>
      </GlassCard>
    );
  }

  const uncertain = !health.label || (health.confidence ?? 0) < 0.60;
  const affected = health.label?.toLowerCase() !== 'healthy';
  return (
    <GlassCard className="p-6">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Leaf Health</p>
      <div className="flex items-baseline gap-3">
        <p className="font-display text-2xl">{uncertain ? 'Uncertain' : affected ? 'Affected / Diseased' : 'Healthy'}</p>
        {health.confidence != null && <GlassBadge tone={bandTone(health.band)}>{Math.round(health.confidence * 100)}%</GlassBadge>}
      </div>
      <p className="mt-2 text-sm text-[var(--ink-soft)]">
        {uncertain ? 'Low confidence image-based prediction.' : affected ? 'Leaf appears affected / diseased.' : 'Image-based AI prediction.'}
      </p>
      <p className="mt-4 text-xs leading-relaxed text-[var(--ink-soft)]">
        This is an image-based AI prediction and is not a professional plant pathology diagnosis. Results may be affected by image quality, lighting, background, and model training coverage.
      </p>
    </GlassCard>
  );
}
