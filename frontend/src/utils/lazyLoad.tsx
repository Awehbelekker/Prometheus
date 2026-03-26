/**
 * Lazy Loading Utilities for Code Splitting
 * 
 * Provides utilities for lazy loading components to reduce initial bundle size.
 * Use these for large components that aren't needed immediately.
 */

import React, { Suspense, ComponentType, LazyExoticComponent } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * Default loading fallback component
 */
export const DefaultLoadingFallback: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '400px',
      gap: 2
    }}
  >
    <CircularProgress size={60} sx={{ color: '#00d4ff' }} />
    <Typography variant="body1" sx={{ color: '#aaa' }}>
      Loading...
    </Typography>
  </Box>
);

/**
 * Minimal loading fallback (for smaller components)
 */
export const MinimalLoadingFallback: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 2
    }}
  >
    <CircularProgress size={40} sx={{ color: '#00d4ff' }} />
  </Box>
);

/**
 * Error fallback component for lazy-loaded components
 */
export const LazyErrorFallback: React.FC<{ error: Error; resetError: () => void }> = ({
  error,
  resetError
}) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '400px',
      gap: 2,
      p: 3
    }}
  >
    <Typography variant="h6" sx={{ color: '#ff6b35' }}>
      Failed to load component
    </Typography>
    <Typography variant="body2" sx={{ color: '#aaa', textAlign: 'center' }}>
      {error.message}
    </Typography>
    <button
      onClick={resetError}
      style={{
        padding: '8px 16px',
        backgroundColor: '#00d4ff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer'
      }}
    >
      Retry
    </button>
  </Box>
);

/**
 * Wrapper for lazy-loaded components with error boundary
 */
export function withLazyLoading<P extends object>(
  Component: LazyExoticComponent<ComponentType<P>>,
  Fallback: React.FC = DefaultLoadingFallback
) {
  return function LazyWrapper(props: P) {
    return (
      <Suspense fallback={<Fallback />}>
        <Component {...props} />
      </Suspense>
    );
  };
}

/**
 * Create a lazy-loaded component with error handling
 * 
 * @example
 * const LazyAdminDashboard = createLazyComponent(
 *   () => import('../components/UnifiedCockpitAdminDashboard'),
 *   'UnifiedCockpitAdminDashboard'
 * );
 */
export function createLazyComponent<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  componentName: string
): LazyExoticComponent<ComponentType<P>> {
  const LazyComponent = React.lazy(importFn);
  
  // Add component name for debugging
  (LazyComponent as any).displayName = `Lazy(${componentName})`;
  
  return LazyComponent;
}

/**
 * Preload a lazy component (useful for prefetching)
 * 
 * @example
 * // Preload admin dashboard when user hovers over admin menu
 * const handleAdminHover = () => {
 *   preloadComponent(() => import('../components/UnifiedCockpitAdminDashboard'));
 * };
 */
export function preloadComponent(
  importFn: () => Promise<{ default: ComponentType<any> }>
): void {
  importFn().catch((error) => {
    console.warn('Failed to preload component:', error);
  });
}

/**
 * Example usage patterns:
 * 
 * 1. Basic lazy loading:
 * ```tsx
 * const LazyAdminDashboard = React.lazy(() => import('./components/UnifiedCockpitAdminDashboard'));
 * 
 * <Suspense fallback={<DefaultLoadingFallback />}>
 *   <LazyAdminDashboard user={user} onLogout={handleLogout} />
 * </Suspense>
 * ```
 * 
 * 2. With error boundary:
 * ```tsx
 * const LazyComponent = createLazyComponent(
 *   () => import('./components/HeavyComponent'),
 *   'HeavyComponent'
 * );
 * 
 * <ErrorBoundary fallback={<LazyErrorFallback />}>
 *   <Suspense fallback={<MinimalLoadingFallback />}>
 *     <LazyComponent {...props} />
 *   </Suspense>
 * </ErrorBoundary>
 * ```
 * 
 * 3. Prefetching on hover:
 * ```tsx
 * <MenuItem
 *   onMouseEnter={() => preloadComponent(() => import('./components/AdminPanel'))}
 *   onClick={() => navigate('/admin')}
 * >
 *   Admin Panel
 * </MenuItem>
 * ```
 */
