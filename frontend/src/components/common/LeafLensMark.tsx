export function LeafLensMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="24" cy="24" r="21" stroke="var(--accent)" strokeWidth="2" opacity="0.35" />
      <circle cx="24" cy="24" r="14.5" stroke="var(--accent)" strokeWidth="1.4" opacity="0.5" />
      <path
        d="M24 10C15 12 10 19 10 27c0 4 2.4 7 6 7 8 0 16-8 16-19 0-2-.3-3.7-1-5-3 0-5.5.6-7 1z"
        fill="var(--accent)"
      />
      <path d="M15 33 25 12" stroke="var(--canvas)" strokeWidth="1.2" strokeLinecap="round" opacity="0.6" />
    </svg>
  );
}
