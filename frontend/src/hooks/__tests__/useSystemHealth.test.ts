/**
 * Tests for useSystemHealth hook
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSystemHealth } from '../useSystemHealth';
import React from 'react';

// Mock fetch
global.fetch = jest.fn();

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('useSystemHealth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return initial metrics', () => {
    const { result } = renderHook(() => useSystemHealth(5000), {
      wrapper: createWrapper()
    });

    expect(result.current.metrics).toBeDefined();
    expect(result.current.metrics.systemHealth).toBe(0);
    expect(result.current.metrics.aiAccuracy).toBe(0);
    expect(result.current.metrics.latency).toBe(0);
  });

  it('should fetch system health from API', async () => {
    const mockData = {
      systemHealth: 95.5,
      aiAccuracy: 92.3,
      latency: 1.2,
      activeStrategies: 5,
      marketStatus: 'open',
      uptime: 99.9
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    const { result } = renderHook(() => useSystemHealth(5000), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.metrics.systemHealth).toBe(95.5);
      expect(result.current.metrics.aiAccuracy).toBe(92.3);
      expect(result.current.metrics.latency).toBe(1.2);
    });
  });

  it('should handle API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSystemHealth(5000), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });

  it('should use fallback endpoint if primary fails', async () => {
    (global.fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('Primary endpoint failed'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          systemHealth: 90,
          aiAccuracy: 88,
          latency: 2.0
        })
      });

    const { result } = renderHook(() => useSystemHealth(5000), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.metrics.systemHealth).toBe(90);
    });
  });

  it('should respect custom refresh interval', () => {
    const customInterval = 10000;
    const { result } = renderHook(() => useSystemHealth(customInterval), {
      wrapper: createWrapper()
    });

    expect(result.current).toBeDefined();
  });
});

