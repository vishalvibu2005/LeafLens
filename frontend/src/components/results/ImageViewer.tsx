import { useState } from 'react';
import type { Analysis, LeafResult } from '../../types/analysis';
import { GlassTabs } from '../glass/Glass';

export function ImageViewer({ analysis, activeLeaf }: { analysis: Analysis; activeLeaf: LeafResult | null }) {
  const tabs = [
    { id: 'original', label: 'Original' },
    { id: 'preprocessed', label: 'Preprocessed' },
    { id: 'detection', label: 'Detection' },
    { id: 'mask', label: 'Mask' },
    ...(activeLeaf ? [{ id: 'segmented', label: 'Segmented' }, { id: 'contours', label: 'Contours' }] : []),
  ];
  const [active, setActive] = useState('detection');

  const srcMap: Record<string, string> = {
    original: analysis.global_views.original,
    preprocessed: analysis.global_views.preprocessed,
    detection: analysis.global_views.detection,
    mask: analysis.global_views.mask,
    segmented: activeLeaf?.views.mask ?? analysis.global_views.mask,
    contours: activeLeaf?.views.contours ?? analysis.global_views.detection,
  };

  return (
    <div className="flex flex-col gap-4">
      <GlassTabs tabs={tabs} active={active} onChange={setActive} />
      <div className="glass overflow-hidden rounded-xl2">
        <img src={srcMap[active]} alt={`${active} view`} className="max-h-[520px] w-full object-contain bg-black/5" />
      </div>
    </div>
  );
}
