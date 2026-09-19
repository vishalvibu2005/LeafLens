import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { LeafLensMark } from '../common/LeafLensMark';
import { ThemeToggle } from './ThemeToggle';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/analyze', label: 'Analyze' },
  { to: '/history', label: 'History' },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-4 z-50 mx-auto max-w-6xl px-4">
      <nav className="glass flex items-center justify-between rounded-full px-4 py-2.5 md:px-6">
        <NavLink to="/" className="flex items-center gap-2 font-display text-lg font-semibold">
          <LeafLensMark size={26} />
          LeafLens
        </NavLink>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors focus-ring ${
                  isActive ? 'text-white' : 'text-[var(--ink-soft)] hover:text-[var(--ink)]'
                }`
              }
              style={({ isActive }) => (isActive ? { backgroundColor: 'var(--accent)' } : {})}
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="hidden md:block">
          <ThemeToggle />
        </div>

        <button
          className="glass-soft rounded-full p-2 md:hidden focus-ring"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </nav>

      {open && (
        <div className="glass mt-2 rounded-2xl p-3 md:hidden">
          <div className="flex flex-col gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `rounded-xl px-3 py-2 text-sm font-medium ${
                    isActive ? 'text-white' : 'text-[var(--ink-soft)]'
                  }`
                }
                style={({ isActive }) => (isActive ? { backgroundColor: 'var(--accent)' } : {})}
              >
                {l.label}
              </NavLink>
            ))}
          </div>
          <div className="leaf-divider my-3" />
          <ThemeToggle />
        </div>
      )}
    </header>
  );
}
