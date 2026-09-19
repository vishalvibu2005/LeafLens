import type { ReactNode, ButtonHTMLAttributes } from 'react';

export function GlassCard({
  children,
  className = '',
  soft = false,
}: {
  children: ReactNode;
  className?: string;
  soft?: boolean;
}) {
  return (
    <div className={`${soft ? 'glass-soft' : 'glass'} rounded-xl2 ${className}`}>{children}</div>
  );
}

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger';
}

export function GlassButton({ children, variant = 'primary', className = '', ...props }: GlassButtonProps) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium transition-all duration-200 focus-ring disabled:opacity-40 disabled:cursor-not-allowed';
  const styles = {
    primary: 'text-white shadow-glass hover:brightness-110 active:scale-[0.98]',
    ghost: 'glass-soft text-ink hover:bg-[var(--surface)] active:scale-[0.98]',
    danger: 'bg-red-500/90 text-white hover:bg-red-500 active:scale-[0.98]',
  };
  const style = variant === 'primary' ? { backgroundColor: 'var(--accent)' } : undefined;
  return (
    <button className={`${base} ${styles[variant]} ${className}`} style={style} {...props}>
      {children}
    </button>
  );
}

export function GlassBadge({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'high' | 'medium' | 'low' | 'demo' }) {
  const tones: Record<string, string> = {
    default: 'bg-[var(--surface-2)] text-[var(--ink-soft)]',
    high: 'bg-[var(--accent)]/15 text-[var(--accent)]',
    medium: 'bg-[var(--accent-2)]/15 text-[var(--accent-2)]',
    low: 'bg-red-500/12 text-red-500',
    demo: 'bg-[var(--accent-2)]/15 text-[var(--accent-2)]',
  };
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function GlassPanel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`glass rounded-xl2 p-6 ${className}`}>{children}</div>;
}

export function GlassTabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { id: string; label: string }[];
  active: string;
  onChange: (id: string) => void;
}) {
  return (
    <div className="glass-soft inline-flex rounded-full p-1 gap-1 scroll-x max-w-full">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={`whitespace-nowrap rounded-full px-4 py-1.5 text-sm font-medium transition-colors focus-ring ${
            active === t.id ? 'text-white' : 'text-[var(--ink-soft)] hover:text-[var(--ink)]'
          }`}
          style={active === t.id ? { backgroundColor: 'var(--accent)' } : undefined}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
