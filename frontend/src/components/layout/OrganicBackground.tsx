export function OrganicBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden" aria-hidden="true">
      <div
        className="absolute -left-40 -top-40 h-[420px] w-[420px] rounded-full blur-3xl opacity-30"
        style={{ background: 'radial-gradient(circle, var(--accent), transparent 70%)' }}
      />
      <div
        className="absolute -right-32 top-1/3 h-[380px] w-[380px] rounded-full blur-3xl opacity-20"
        style={{ background: 'radial-gradient(circle, var(--accent-2), transparent 70%)' }}
      />
      <div
        className="absolute bottom-[-200px] left-1/4 h-[500px] w-[500px] rounded-full blur-3xl opacity-20"
        style={{ background: 'radial-gradient(circle, var(--accent), transparent 70%)' }}
      />
      <svg className="absolute inset-0 h-full w-full opacity-[0.035]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="focus-ring-pattern" width="120" height="120" patternUnits="userSpaceOnUse">
            <circle cx="60" cy="60" r="38" fill="none" stroke="var(--ink)" strokeWidth="1" />
            <circle cx="60" cy="60" r="2" fill="var(--ink)" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#focus-ring-pattern)" />
      </svg>
    </div>
  );
}
