/**
 * useOptimizedQuery Hook
 * Optimized data fetching with intelligent caching and performance monitoring
 */

import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import { measureApiCall, isSlowConnection } from '../utils/performance';

interface OptimizedQueryOptions<TData, TError> extends Omit<UseQueryOptions<TData, TError>, 'queryKey' | 'queryFn'> {
  // Custom options
  enableSlowConnectionOptimization?: boolean;
  logPerformance?: boolean;
}

/**
 * Enhanced useQuery with performance optimizations
 */
export const useOptimizedQuery = <TData = unknown, TError = unknown>(
  queryKey: string[],
  queryFn: () => Promise<TData>,
  options: OptimizedQueryOptions<TData, TError> = {}
): UseQueryResult<TData, TError> => {
  const {
    enableSlowConnectionOptimization = true,
    logPerformance = process.env.NODE_ENV === 'development',
    ...queryOptions
  } = options;

  // Adjust settings for slow connections
  const isSlowConn = enableSlowConnectionOptimization && isSlowConnection();

  const optimizedOptions: UseQueryOptions<TData, TError> = {
    ...queryOptions,
    queryKey,
    queryFn: async () => {
      if (logPerformance) {
        return measureApiCall(queryKey.join('/'), queryFn);
      }
      return queryFn();
    },
    // Optimize for slow connections
    staleTime: isSlowConn ? 300000 : (queryOptions.staleTime ?? 30000), // 5 min vs 30 sec
    gcTime: isSlowConn ? 600000 : 300000, // 10 min vs 5 min (renamed from cacheTime)
    refetchOnWindowFocus: isSlowConn ? false : (queryOptions.refetchOnWindowFocus ?? true),
    refetchOnReconnect: isSlowConn ? false : (queryOptions.refetchOnReconnect ?? true),
    retry: isSlowConn ? 1 : (queryOptions.retry ?? 3)
  };

  return useQuery(optimizedOptions);
};

/**
 * Hook for paginated queries with optimized prefetching
 */
export const useOptimizedPaginatedQuery = <TData = unknown, TError = unknown>(
  queryKey: string[],
  queryFn: (page: number) => Promise<TData>,
  page: number,
  options: OptimizedQueryOptions<TData, TError> = {}
): UseQueryResult<TData, TError> => {
  const result = useOptimizedQuery<TData, TError>(
    [...queryKey, `page-${page}`],
    () => queryFn(page),
    options
  );

  // Prefetch next page
  // Note: This would require access to queryClient, which should be passed as an option
  // For now, this is a placeholder for the concept

  return result;
};

/**
 * Hook for infinite scroll queries
 */
export const useOptimizedInfiniteQuery = <TData = unknown, TError = unknown>(
  queryKey: string[],
  queryFn: (pageParam: number) => Promise<TData>,
  options: OptimizedQueryOptions<TData, TError> = {}
) => {
  // This would use useInfiniteQuery from React Query
  // Placeholder for the concept
  return useOptimizedQuery<TData, TError>(
    queryKey,
    () => queryFn(0),
    options
  );
};

export default useOptimizedQuery;

