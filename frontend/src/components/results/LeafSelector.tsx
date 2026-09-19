import type { LeafResult } from '../../types/analysis';

export function LeafSelector({
  leaves,
  activeId,
  onSelect,
}: {
  leaves: LeafResult[];
  activeId: number;
  onSelect: (id: number) => void;
}) {
  if (leaves.length <= 1) return null;
  return (
    <div className="glass-soft flex flex-wrap gap-2 rounded-full p-1.5">
      <span className="px-2 py-1 text-xs font-medium text-[var(--ink-soft)]">
        {leaves.length} leaves detected
      </span>
      {leaves.map((l) => (
        <button
          key={l.leaf_id}
          onClick={() => onSelect(l.leaf_id)}
          className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors focus-ring ${
            activeId === l.leaf_id ? 'text-white' : 'text-[var(--ink-soft)] hover:text-[var(--ink)]'
          }`}
          style={activeId === l.leaf_id ? { backgroundColor: 'var(--accent)' } : undefined}
        >
          Leaf {l.leaf_id}
        </button>
      ))}
    </div>
  );
}
