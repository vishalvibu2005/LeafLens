import type { Analysis, HealthStatus, DashboardStats, ApiError } from '../types/analysis';

const BASE = '/api';

class LeafLensApiError extends Error {
  code: string;
  constructor(err: ApiError) {
    super(err.message);
    this.code = err.code;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail: ApiError = { code: 'UNKNOWN', message: 'Something went wrong.' };
    try {
      const body = await res.json();
      detail = body.detail ?? body;
    } catch {
      /* ignore parse errors */
    }
    throw new LeafLensApiError(detail);
  }
  return res.json();
}

export const api = {
  health: () => fetch(`${BASE}/health`).then((r) => handle<HealthStatus>(r)),

  analyze: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/analyze`, { method: 'POST', body: form }).then((r) => handle<Analysis>(r));
  },

  history: (params?: { search?: string; leaf_type?: string; growth_stage?: string; health_status?: string; sort?: string }) => {
    const qs = new URLSearchParams(
      Object.entries(params ?? {}).filter(([, value]) => value != null) as [string, string][]
    ).toString();
    return fetch(`${BASE}/history${qs ? `?${qs}` : ''}`).then((r) => handle<Analysis[]>(r));
  },

  historyItem: (id: string) => fetch(`${BASE}/history/${id}`).then((r) => handle<Analysis>(r)),

  deleteHistoryItem: (id: string) =>
    fetch(`${BASE}/history/${id}`, { method: 'DELETE' }).then((r) => handle<{ deleted: boolean }>(r)),

  deleteAllHistory: () =>
    fetch(`${BASE}/history`, { method: 'DELETE' }).then((r) => handle<{ deleted: number }>(r)),

  dashboardStats: () => fetch(`${BASE}/dashboard/stats`).then((r) => handle<DashboardStats>(r)),
};

export { LeafLensApiError };
