import { useEffect, useState } from 'react';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';

interface FeatureAvailabilityResponse {
  success: boolean;
  generated_at: string;
  features: Record<string, boolean>;
  missing: string[];
  notes?: string;
  feature_modes?: Record<string,string>;
  fallback?: string[];
}

interface FeatureDetailResponse {
  success: boolean;
  generated_at: string;
  detail: Record<string, {available: boolean; mode: string; usage_count: number}>;
}

export function useFeatureAvailability(pollMs: number = 60000) {
  const [data, setData] = useState<FeatureAvailabilityResponse | null>(null);
  const [detail, setDetail] = useState<FeatureDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const [availJson, detailJson] = await Promise.all([
        getJsonWithRetry<any>(getApiUrl('/api/features/availability'), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 6000 }),
        getJsonWithRetry<any>(getApiUrl('/api/features/detail'), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 6000 }).catch(() => null as any)
      ]);
      setData(availJson);
      if (detailJson && detailJson.success) setDetail(detailJson);
    } catch (e: any) {
      setError(e.message || 'Failed to load feature availability');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    if (pollMs > 0) {
      const id = setInterval(load, pollMs);
      return () => clearInterval(id);
    }
  }, [pollMs]);

  return { data, detail, error, loading, reload: load };
}

export function useIsFeatureAvailable(name: string) {
  const { data } = useFeatureAvailability();
  return !!data?.features?.[name];
}
