/**
 * Tests for useUserPortfolio hook
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUserPortfolio } from '../useUserPortfolio';
import React from 'react';

// Mock apiCall
jest.mock('../../config/api', () => ({
  apiCall: jest.fn()
}));

import { apiCall } from '../../config/api';

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

describe('useUserPortfolio', () => {
  const mockUserId = 'user123';
  const mockPortfolio = {
    totalValue: 100000,
    cashBalance: 20000,
    totalReturn: 15000,
    returnPercentage: 15,
    positions: [
      {
        symbol: 'AAPL',
        quantity: 10,
        avgPrice: 150,
        currentPrice: 160,
        totalValue: 1600,
        profitLoss: 100,
        returnPercentage: 6.67
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch portfolio data successfully', async () => {
    (apiCall as jest.Mock).mockResolvedValueOnce(mockPortfolio);

    const { result } = renderHook(() => useUserPortfolio(mockUserId), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.portfolio).toEqual(mockPortfolio);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  it('should handle API errors', async () => {
    (apiCall as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => useUserPortfolio(mockUserId), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
      expect(result.current.portfolio).toBeNull();
    });
  });

  it('should not fetch when enabled is false', () => {
    const { result } = renderHook(() => useUserPortfolio(mockUserId, false), {
      wrapper: createWrapper()
    });

    expect(apiCall).not.toHaveBeenCalled();
    expect(result.current.portfolio).toBeNull();
  });

  it('should refetch portfolio data', async () => {
    (apiCall as jest.Mock).mockResolvedValue(mockPortfolio);

    const { result } = renderHook(() => useUserPortfolio(mockUserId), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.portfolio).toEqual(mockPortfolio);
    });

    // Trigger refetch
    result.current.refetch();

    await waitFor(() => {
      expect(apiCall).toHaveBeenCalledTimes(2);
    });
  });

  it('should cache portfolio data', async () => {
    (apiCall as jest.Mock).mockResolvedValueOnce(mockPortfolio);

    const { result, rerender } = renderHook(() => useUserPortfolio(mockUserId), {
      wrapper: createWrapper()
    });

    await waitFor(() => {
      expect(result.current.portfolio).toEqual(mockPortfolio);
    });

    // Rerender should use cached data
    rerender();

    expect(apiCall).toHaveBeenCalledTimes(1);
  });
});

