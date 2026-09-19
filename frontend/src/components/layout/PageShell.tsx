import type { ReactNode } from 'react';
import { Navbar } from '../navigation/Navbar';
import { OrganicBackground } from './OrganicBackground';

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen font-body">
      <OrganicBackground />
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 pb-24 pt-10 md:pt-14">{children}</main>
    </div>
  );
}
