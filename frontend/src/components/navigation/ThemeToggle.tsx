import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

const options = [
  { id: 'light' as const, icon: Sun, label: 'Light' },
  { id: 'system' as const, icon: Monitor, label: 'System' },
  { id: 'dark' as const, icon: Moon, label: 'Dark' },
];

export function ThemeToggle() {
  const { mode, setMode } = useTheme();
  return (
    <div className="glass-soft inline-flex rounded-full p-1 gap-0.5">
      {options.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          aria-label={`${label} theme`}
          onClick={() => setMode(id)}
          className={`rounded-full p-1.5 transition-colors focus-ring ${
            mode === id ? 'text-white' : 'text-[var(--ink-soft)] hover:text-[var(--ink)]'
          }`}
          style={mode === id ? { backgroundColor: 'var(--accent)' } : undefined}
        >
          <Icon size={15} />
        </button>
      ))}
    </div>
  );
}
