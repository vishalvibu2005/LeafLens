import type { LeafResult } from '../../types/analysis';
import { GlassCard } from '../glass/Glass';

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--border)] py-2 text-sm last:border-0">
      <span className="text-[var(--ink-soft)]">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export function FeatureDashboard({ leaf }: { leaf: LeafResult }) {
  const { shape, color, texture } = leaf;
  return (
    <div className="grid gap-5 md:grid-cols-3">
      <GlassCard soft className="p-5">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Shape</p>
        <Row label="Area" value={`${shape.area.toLocaleString()} px²`} />
        <Row label="Perimeter" value={`${shape.perimeter.toFixed(0)} px`} />
        <Row label="Width" value={`${shape.width} px`} />
        <Row label="Height" value={`${shape.height} px`} />
        <Row label="Aspect ratio" value={shape.aspect_ratio.toFixed(2)} />
        <Row label="Circularity" value={shape.circularity.toFixed(2)} />
        <Row label="Solidity" value={shape.solidity.toFixed(2)} />
        <Row label="Extent" value={shape.extent.toFixed(2)} />
      </GlassCard>

      <GlassCard soft className="p-5">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Color</p>
        <div className="mb-4 flex items-center gap-3">
          <div
            className="h-12 w-12 rounded-xl border border-[var(--border)]"
            style={{ backgroundColor: `rgb(${color.rgb.r}, ${color.rgb.g}, ${color.rgb.b})` }}
          />
          <div className="text-sm">
            <p className="font-medium">{color.dominant_color ?? '—'}</p>
            <p className="text-[var(--ink-soft)]">
              RGB {Math.round(color.rgb.r)}, {Math.round(color.rgb.g)}, {Math.round(color.rgb.b)}
            </p>
          </div>
        </div>
        <Row label="Mean R" value={color.rgb.r.toFixed(1)} />
        <Row label="Mean G" value={color.rgb.g.toFixed(1)} />
        <Row label="Mean B" value={color.rgb.b.toFixed(1)} />
      </GlassCard>

      <GlassCard soft className="p-5">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--ink-soft)]">Texture</p>
        <Row label="Contrast" value={texture.contrast.toFixed(2)} />
        <Row label="Homogeneity" value={texture.homogeneity.toFixed(2)} />
        <Row label="Energy" value={texture.energy.toFixed(2)} />
        <Row label="Correlation" value={texture.correlation.toFixed(2)} />
      </GlassCard>
    </div>
  );
}
