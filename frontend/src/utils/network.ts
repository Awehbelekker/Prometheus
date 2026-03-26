// Lightweight fetch retry utilities with exponential backoff and optional timeout
// Centralize resilience so components avoid duplicating retry logic

export interface RetryOptions {
  retries?: number;            // total attempts including the first (default 3)
  backoffMs?: number;          // base backoff in ms (default 500)
  maxBackoffMs?: number;       // cap for backoff (default 8000)
  timeoutMs?: number;          // per-attempt timeout (optional)
  // Whether to retry on a given error/response. Default: retry on 429/5xx and network errors
  shouldRetry?: (error: unknown, response?: Response) => boolean;
}

const defaultShouldRetry = (error: unknown, response?: Response) => {
  // Network errors (TypeError from fetch) should retry
  if (error && (error as any).name === 'AbortError') return true; // timeout treated as retryable
  if (error && (error as any).message && (error as any).message.includes('NetworkError')) return true;
  if (response) {
    if (response.status === 429) return true;
    if (response.status >= 500) return true;
  }
  return false;
};

function sleep(ms: number) {
  return new Promise((res) => setTimeout(res, ms));
}

export async function fetchWithRetry(input: RequestInfo | URL, init: RequestInit = {}, opts: RetryOptions = {}): Promise<Response> {
  const {
    retries = 3,
    backoffMs = 500,
    maxBackoffMs = 8000,
    timeoutMs,
    shouldRetry = defaultShouldRetry,
  } = opts;

  let attempt = 0;
  let lastError: unknown;

  while (attempt < retries) {
    const controller = timeoutMs ? new AbortController() : undefined;
    const timer = timeoutMs ? setTimeout(() => controller!.abort(), timeoutMs) : undefined;

    try {
      const response = await fetch(input, { ...init, signal: controller?.signal });
      if (!response.ok) {
        if (attempt < retries - 1 && shouldRetry(null, response)) {
          attempt++;
          const base = Math.min(backoffMs * Math.pow(2, attempt - 1), maxBackoffMs);
          const jitter = Math.random() * 250;
          await sleep(base + jitter);
          continue;
        }
      }
      return response;
    } catch (err) {
      lastError = err;
      if (!(attempt < retries - 1 && shouldRetry(err))) {
        throw err;
      }
      attempt++;
      const base = Math.min(backoffMs * Math.pow(2, attempt - 1), maxBackoffMs);
      const jitter = Math.random() * 250;
      await sleep(base + jitter);
    } finally {
      if (timer) clearTimeout(timer);
    }
  }

  throw lastError ?? new Error('fetchWithRetry: exhausted retries');
}

export async function getJsonWithRetry<T = any>(input: RequestInfo | URL, init: RequestInit = {}, opts: RetryOptions = {}): Promise<T> {
  const res = await fetchWithRetry(input, init, opts);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${res.statusText}${text ? ` - ${text}` : ''}`);
  }
  return res.json() as Promise<T>;
}

