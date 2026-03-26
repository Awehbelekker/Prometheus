import { fetchWithRetry, getJsonWithRetry } from '../utils/network';

// Helper to mock global fetch
const mockFetch = (impl: jest.Mock) => {
  // @ts-ignore
  global.fetch = impl;
};

describe('network resilience utils', () => {
  beforeEach(() => {
    jest.spyOn(global.Math, 'random').mockReturnValue(0); // eliminate jitter randomness
  });
  afterEach(() => {
    // @ts-ignore
    global.fetch && (global.fetch as jest.Mock).mockReset?.();
    (global.Math.random as jest.Mock).mockRestore();
  });

  test('fetchWithRetry retries on 500 and succeeds', async () => {
    const responses = [
      new Response('err', { status: 500 }),
      new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    ];
    const impl = jest.fn().mockImplementation(() => Promise.resolve(responses.shift()!));
    mockFetch(impl);

    const p = fetchWithRetry('/api/test', {}, { retries: 2, backoffMs: 0, maxBackoffMs: 0, timeoutMs: 100 });
    const res = await p;

    expect(res.ok).toBe(true);
    expect((global.fetch as jest.Mock).mock.calls.length).toBe(2);
  });

  test('getJsonWithRetry throws on non-ok after retries', async () => {
    const impl = jest.fn().mockResolvedValue(new Response('nope', { status: 500 }));
    mockFetch(impl);

    const p = getJsonWithRetry('/api/test', {}, { retries: 2, backoffMs: 0, maxBackoffMs: 0, timeoutMs: 50 });
    await expect(async () => {
      await p;
    }).rejects.toThrow(/HTTP 500/);
    expect((global.fetch as jest.Mock).mock.calls.length).toBeGreaterThanOrEqual(2);
  });
});

