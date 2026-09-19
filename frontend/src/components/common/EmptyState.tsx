import type { ReactNode } from 'react';

export function EmptyState({ icon, title, subtitle, action }: { icon?: ReactNode; title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="glass rounded-xl2 flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      {icon}
      <p className="font-display text-xl">{title}</p>
      {subtitle && <p className="max-w-sm text-sm text-[var(--ink-soft)]">{subtitle}</p>}
      {action}
    </div>
  );
}
