import { useCallback, useEffect, useRef, useState } from 'react';
import { Camera, RefreshCw, Video, X } from 'lucide-react';
import { GlassButton } from '../glass/Glass';

interface Props { onUseImage: (file: File) => void; }
function friendlyCameraError(error: unknown): string {
  const name = error instanceof DOMException ? error.name : '';
  if (name === 'NotAllowedError' || name === 'SecurityError') return 'Camera permission was denied. Please allow camera access and try again.';
  if (name === 'NotFoundError' || name === 'OverconstrainedError') return 'Camera is not available on this device.';
  if (name === 'NotReadableError') return 'Camera is already in use by another application.';
  return 'Unable to open the camera. Camera capture may require HTTPS or localhost.';
}

export function CameraCapture({ onUseImage }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null); const streamRef = useRef<MediaStream | null>(null);
  const [open, setOpen] = useState(false); const [captured, setCaptured] = useState<File | null>(null); const [preview, setPreview] = useState<string | null>(null); const [error, setError] = useState<string | null>(null);
  const stopCamera = useCallback(() => { streamRef.current?.getTracks().forEach((track) => track.stop()); streamRef.current = null; if (videoRef.current) videoRef.current.srcObject = null; }, []);
  const openCamera = useCallback(async () => {
    setError(null); setCaptured(null);
    if (!navigator.mediaDevices?.getUserMedia) { setError('Your browser does not support camera capture.'); return; }
    try { const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false }); streamRef.current = stream; setOpen(true); requestAnimationFrame(() => { if (videoRef.current) videoRef.current.srcObject = stream; }); }
    catch (cameraError) { setError(friendlyCameraError(cameraError)); }
  }, []);
  useEffect(() => () => { stopCamera(); if (preview) URL.revokeObjectURL(preview); }, [preview, stopCamera]);
  const capture = () => {
    const video = videoRef.current; if (!video || !video.videoWidth || !video.videoHeight) return;
    const canvas = document.createElement('canvas'); canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => { if (!blob) { setError('Unable to capture an image. Please try again.'); return; } const file = new File([blob], `leaflens-camera-${Date.now()}.jpg`, { type: 'image/jpeg' }); if (preview) URL.revokeObjectURL(preview); setPreview(URL.createObjectURL(file)); setCaptured(file); stopCamera(); }, 'image/jpeg', 0.92);
  };
  const close = () => { stopCamera(); setOpen(false); setCaptured(null); if (preview) URL.revokeObjectURL(preview); setPreview(null); };
  const retake = () => { if (preview) URL.revokeObjectURL(preview); setPreview(null); setCaptured(null); openCamera(); };
  if (!open && !captured) return <div className="glass flex min-h-[290px] flex-col items-center justify-center rounded-xl2 p-6 text-center"><Camera size={36} className="mb-4" style={{ color: 'var(--accent)' }} /><p className="font-display text-xl">Take Image</p><p className="mt-1 text-sm text-[var(--ink-soft)]">Capture a leaf with your camera</p><GlassButton className="mt-6" onClick={openCamera} aria-label="Open camera"><Video size={16} />Open Camera</GlassButton>{error && <p role="alert" className="mt-4 text-sm text-red-500">{error}</p>}</div>;
  return <div className="glass rounded-xl2 p-5 md:p-6">{!captured ? <><div className="mb-4 flex items-center justify-between"><p className="font-display text-xl">Live Camera</p><button onClick={close} aria-label="Close camera" className="rounded-full p-2 text-[var(--ink-soft)] focus-ring"><X size={18} /></button></div><video ref={videoRef} autoPlay playsInline muted aria-label="Live camera preview" className="aspect-[4/3] w-full rounded-xl bg-black object-cover" /><div className="mt-4 flex flex-wrap gap-3"><GlassButton onClick={capture} aria-label="Capture image"><Camera size={16} />Capture Image</GlassButton><GlassButton variant="ghost" onClick={close}>Close Camera</GlassButton></div></> : <><p className="mb-4 font-display text-xl">Captured Leaf</p><img src={preview ?? ''} alt="Captured leaf preview" className="aspect-[4/3] w-full rounded-xl bg-black/5 object-contain" /><div className="mt-4 flex flex-wrap gap-3"><GlassButton variant="ghost" onClick={retake}><RefreshCw size={16} />Retake</GlassButton><GlassButton onClick={() => { if (captured) { onUseImage(captured); close(); } }}>Use This Image</GlassButton></div></>}{error && <p role="alert" className="mt-4 text-sm text-red-500">{error}</p>}</div>;
}
