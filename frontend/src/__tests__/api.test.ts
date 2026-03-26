import { apiCall, API_BASE_URL } from '../config/api';

const setupFetch = (fn: jest.Mock) => {
  // @ts-ignore
  global.fetch = fn;
};

describe('apiCall helper', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('attaches Authorization header when token present', async () => {
    localStorage.setItem('authToken', 'abc');

    const fetchMock = jest.fn().mockImplementation((url: RequestInfo, init?: RequestInit) => {
      expect(url).toBe(`${API_BASE_URL}/x`);
      expect(init?.headers).toMatchObject({ Authorization: 'Bearer abc' });
      return Promise.resolve(new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }));
    });
    setupFetch(fetchMock);

    const res = await apiCall('/x');
    expect(res).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('throws on non-ok status', async () => {
    const fetchMock = jest.fn().mockResolvedValue(new Response('bad', { status: 500 }));
    setupFetch(fetchMock);
    await expect(apiCall('/x')).rejects.toThrow(/HTTP 500|failed/i);
  });
});

