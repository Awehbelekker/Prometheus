/**
 * Performance Monitoring Utilities
 * Track and optimize frontend performance
 */

/**
 * Measure component render time
 */
export const measureRenderTime = (componentName: string) => {
  const startTime = performance.now();

  return () => {
    const endTime = performance.now();
    const renderTime = endTime - startTime;

    if (renderTime > 16) {
      // Warn if render takes longer than one frame (16ms at 60fps)
      console.warn(
        `[Performance] ${componentName} took ${renderTime.toFixed(2)}ms to render`
      );
    }

    return renderTime;
  };
};

/**
 * Debounce function for performance optimization
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }

    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
};

/**
 * Throttle function for performance optimization
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean = false;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;

      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
};

/**
 * Measure API call performance
 */
export const measureApiCall = async <T>(
  apiName: string,
  apiCall: () => Promise<T>
): Promise<T> => {
  const startTime = performance.now();

  try {
    const result = await apiCall();
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.log(`[API Performance] ${apiName} took ${duration.toFixed(2)}ms`);

    // Log slow API calls
    if (duration > 1000) {
      console.warn(`[API Performance] Slow API call: ${apiName} (${duration.toFixed(2)}ms)`);
    }

    return result;
  } catch (error) {
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.error(
      `[API Performance] ${apiName} failed after ${duration.toFixed(2)}ms`,
      error
    );

    throw error;
  }
};

/**
 * Get Web Vitals metrics
 */
export const getWebVitals = () => {
  if ('performance' in window && 'getEntriesByType' in performance) {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType('paint');

    return {
      // Time to First Byte
      ttfb: navigation?.responseStart - navigation?.requestStart,
      // First Contentful Paint
      fcp: paint.find((entry) => entry.name === 'first-contentful-paint')?.startTime,
      // DOM Content Loaded
      dcl: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
      // Load Complete
      loadComplete: navigation?.loadEventEnd - navigation?.loadEventStart,
      // Total Page Load Time
      totalLoadTime: navigation?.loadEventEnd - navigation?.fetchStart
    };
  }

  return null;
};

/**
 * Log Web Vitals to console
 */
export const logWebVitals = () => {
  const vitals = getWebVitals();

  if (vitals) {
    console.group('[Web Vitals]');
    console.log(`TTFB: ${vitals.ttfb?.toFixed(2)}ms`);
    console.log(`FCP: ${vitals.fcp?.toFixed(2)}ms`);
    console.log(`DCL: ${vitals.dcl?.toFixed(2)}ms`);
    console.log(`Load Complete: ${vitals.loadComplete?.toFixed(2)}ms`);
    console.log(`Total Load Time: ${vitals.totalLoadTime?.toFixed(2)}ms`);
    console.groupEnd();
  }
};

/**
 * Memoization utility for expensive computations
 */
export const memoize = <T extends (...args: any[]) => any>(
  func: T
): T => {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = func(...args);
    cache.set(key, result);

    return result;
  }) as T;
};

/**
 * Check if user is on slow connection
 */
export const isSlowConnection = (): boolean => {
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;
    
    if (connection) {
      // Check for slow connection types
      const slowConnectionTypes = ['slow-2g', '2g', '3g'];
      
      if (slowConnectionTypes.includes(connection.effectiveType)) {
        return true;
      }

      // Check for save-data mode
      if (connection.saveData) {
        return true;
      }
    }
  }

  return false;
};

/**
 * Prefetch resource
 */
export const prefetchResource = (url: string, type: 'script' | 'style' | 'image' = 'script') => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  link.as = type;
  document.head.appendChild(link);
};

/**
 * Preload critical resource
 */
export const preloadResource = (url: string, type: 'script' | 'style' | 'image' = 'script') => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = url;
  link.as = type;
  document.head.appendChild(link);
};

/**
 * Monitor long tasks (tasks that block main thread for >50ms)
 */
export const monitorLongTasks = () => {
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.warn(
            `[Performance] Long task detected: ${entry.duration.toFixed(2)}ms`,
            entry
          );
        }
      });

      observer.observe({ entryTypes: ['longtask'] });

      return () => observer.disconnect();
    } catch (e) {
      console.warn('[Performance] Long task monitoring not supported');
    }
  }

  return () => {};
};

/**
 * Get memory usage (Chrome only)
 */
export const getMemoryUsage = () => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    
    return {
      usedJSHeapSize: (memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
      totalJSHeapSize: (memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
      jsHeapSizeLimit: (memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
    };
  }

  return null;
};

export default {
  measureRenderTime,
  debounce,
  throttle,
  measureApiCall,
  getWebVitals,
  logWebVitals,
  memoize,
  isSlowConnection,
  prefetchResource,
  preloadResource,
  monitorLongTasks,
  getMemoryUsage
};

