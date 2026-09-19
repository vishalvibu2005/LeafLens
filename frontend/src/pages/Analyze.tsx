import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageShell } from '../components/layout/PageShell';
import { UploadPanel } from '../components/upload/UploadPanel';
import { CameraCapture } from '../components/camera/CameraCapture';
import { ProcessingPipeline } from '../components/analysis/ProcessingPipeline';
import { GlassBadge, GlassCard } from '../components/glass/Glass';
import { api, LeafLensApiError } from '../services/api';
import type { HealthStatus } from '../types/analysis';

export function Analyze() {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelStatus, setModelStatus] = useState<HealthStatus | null>(null);
  const navigate = useNavigate();

  useEffect(() => { api.health().then(setModelStatus).catch(() => setModelStatus(null)); }, []);

  const handleAnalyze = async (selectedFile: File) => {
    setBusy(true); setError(null);
    try {
      const result = await api.analyze(selectedFile);
      navigate(`/results/${result.analysis_id}`, { state: result });
    } catch (exception) {
      setError(exception instanceof LeafLensApiError ? exception.message : 'Analysis failed. Please try again.');
    } finally { setBusy(false); }
  };

  return (
    <PageShell>
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-2 font-display text-3xl">Analyze a Leaf</h1>
        <p className="mb-5 text-[var(--ink-soft)]">Upload a leaf image or capture one using your camera.</p>
        {modelStatus && (
          <div className="mb-6 flex flex-wrap items-center gap-2 text-xs text-[var(--ink-soft)]">
            <span className="mr-1 font-medium uppercase tracking-wide">AI models</span>
            <GlassBadge tone={modelStatus.models.leaf_classifier ? 'high' : 'demo'}>Species {modelStatus.models.leaf_classifier ? 'available' : 'unavailable'}</GlassBadge>
            <GlassBadge tone={modelStatus.models.health_classifier ? 'high' : 'demo'}>Health {modelStatus.models.health_classifier ? 'available' : 'unavailable'}</GlassBadge>
            <GlassBadge tone={modelStatus.models.stage_classifier ? 'high' : 'demo'}>Growth stage {modelStatus.models.stage_classifier ? 'available' : 'unavailable'}</GlassBadge>
          </div>
        )}
        {busy ? <ProcessingPipeline /> : file ? (
          <UploadPanel file={file} onFileChange={setFile} onAnalyze={handleAnalyze} busy={busy} />
        ) : (
          <div className="grid gap-5 md:grid-cols-2">
            <UploadPanel file={null} onFileChange={setFile} onAnalyze={handleAnalyze} busy={busy} />
            <CameraCapture onUseImage={setFile} />
          </div>
        )}
        {error && <GlassCard className="mt-6 p-5 text-sm text-red-500">{error}</GlassCard>}
      </div>
    </PageShell>
  );
}
