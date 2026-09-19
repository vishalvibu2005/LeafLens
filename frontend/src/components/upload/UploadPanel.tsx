import { useCallback, useEffect, useRef, useState } from 'react';
import { ImageIcon, UploadCloud, X } from 'lucide-react';
import { GlassButton } from '../glass/Glass';

const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_MB = 10;

interface Props {
  file: File | null;
  onFileChange: (file: File | null) => void;
  onAnalyze: (file: File) => void;
  busy: boolean;
}

/** Upload and camera both feed this same selected File state. */
export function UploadPanel({ file, onFileChange, onAnalyze, busy }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [dims, setDims] = useState<{ w: number; h: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) { setPreview(null); setDims(null); return; }
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => setDims({ w: image.width, h: image.height });
    image.src = url;
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleFile = useCallback((candidate: File) => {
    setError(null);
    if (!ACCEPTED.includes(candidate.type)) { setError('Unsupported format. Please use JPG, PNG, or WEBP.'); return; }
    if (candidate.size > MAX_MB * 1024 * 1024) { setError(`File is too large. Maximum size is ${MAX_MB}MB.`); return; }
    onFileChange(candidate);
  }, [onFileChange]);

  const fileInput = <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(event) => event.target.files?.[0] && handleFile(event.target.files[0])} />;

  if (!file || !preview) return (
    <div onDragOver={(event) => { event.preventDefault(); setDragOver(true); }} onDragLeave={() => setDragOver(false)} onDrop={(event) => { event.preventDefault(); setDragOver(false); const dropped = event.dataTransfer.files?.[0]; if (dropped) handleFile(dropped); }} className={`glass flex min-h-[290px] flex-col items-center justify-center rounded-xl2 border-2 border-dashed p-6 text-center transition-colors ${dragOver ? 'border-[var(--accent)] bg-[var(--surface-2)]' : 'border-[var(--border)]'}`}>
      <UploadCloud size={36} className="mb-4" style={{ color: 'var(--accent)' }} />
      <p className="font-display text-xl">Upload Image</p>
      <p className="mt-1 text-sm text-[var(--ink-soft)]">Drop a leaf image or browse from your device</p>
      {fileInput}<GlassButton className="mt-6" onClick={() => inputRef.current?.click()}>Choose Image</GlassButton>
      <p className="mt-5 text-xs text-[var(--ink-soft)]">JPG, PNG, WEBP · Maximum {MAX_MB}MB</p>
      {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
    </div>
  );

  return (
    <div className="glass rounded-xl2 p-6 md:p-8"><div className="flex flex-col gap-5">
      <div className="relative overflow-hidden rounded-xl"><img src={preview} alt="Selected leaf preview" className="max-h-[420px] w-full bg-black/5 object-contain" /><button onClick={() => onFileChange(null)} aria-label="Remove image" className="absolute right-3 top-3 rounded-full bg-black/50 p-1.5 text-white hover:bg-black/70 focus-ring"><X size={16} /></button></div>
      <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-[var(--ink-soft)]"><span className="flex items-center gap-2"><ImageIcon size={15} />{file.name} {dims && `· ${dims.w}×${dims.h}px`} · {(file.size / 1024).toFixed(0)}KB</span></div>
      <div className="flex flex-wrap gap-3"><GlassButton disabled={busy} onClick={() => onAnalyze(file)}>{busy ? 'Analyzing…' : 'Analyze Leaf'}</GlassButton><GlassButton variant="ghost" onClick={() => inputRef.current?.click()} disabled={busy}>Replace Image</GlassButton><GlassButton variant="ghost" onClick={() => onFileChange(null)} disabled={busy}>Clear</GlassButton>{fileInput}</div>
    </div>{error && <p className="mt-4 text-sm text-red-500">{error}</p>}</div>
  );
}
