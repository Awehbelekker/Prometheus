import React, { useEffect, useState } from 'react';

interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  cacheHitRate: number;
  serviceWorkerStatus: string;
  memoryUsage: number;
  networkRequests: number;
}

export const PerformanceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    loadTime: 0,
    renderTime: 0,
    cacheHitRate: 0,
    serviceWorkerStatus: 'Unknown',
    memoryUsage: 0,
    networkRequests: 0
  });

  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show in development or when debug mode is enabled
    const showMonitor = process.env.NODE_ENV === 'development' || 
                       process.env.REACT_APP_DEBUG_MODE === 'true';
    setIsVisible(showMonitor);

    if (!showMonitor) return;

    const updateMetrics = () => {
      // Performance timing
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const loadTime = navigation.loadEventEnd - navigation.fetchStart;
      const renderTime = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;

      // Memory usage (if available)
      const memory = (performance as any).memory;
      const memoryUsage = memory ? memory.usedJSHeapSize / 1024 / 1024 : 0;

      // Service Worker status
      let serviceWorkerStatus = 'Not Available';
      if ('serviceWorker' in navigator) {
        if (navigator.serviceWorker.controller) {
          serviceWorkerStatus = 'Active';
        } else {
          serviceWorkerStatus = 'Registered';
        }
      }

      // Network requests count
      const resourceEntries = performance.getEntriesByType('resource');
      const networkRequests = resourceEntries.length;

      // Cache hit rate estimation (simplified)
      const cachedRequests = resourceEntries.filter(entry => 
        (entry as PerformanceResourceTiming).transferSize === 0
      ).length;
      const cacheHitRate = networkRequests > 0 ? (cachedRequests / networkRequests) * 100 : 0;

      setMetrics({
        loadTime: Math.round(loadTime),
        renderTime: Math.round(renderTime),
        cacheHitRate: Math.round(cacheHitRate),
        serviceWorkerStatus,
        memoryUsage: Math.round(memoryUsage),
        networkRequests
      });
    };

    // Update metrics initially and then every 5 seconds
    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.8)',
      color: '#00d4ff',
      padding: '10px',
      borderRadius: '5px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999,
      minWidth: '200px',
      border: '1px solid #00d4ff'
    }}>
      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
        🚀 PROMETHEUS Performance
      </div>
      <div>Load Time: {metrics.loadTime}ms</div>
      <div>Render Time: {metrics.renderTime}ms</div>
      <div>Cache Hit Rate: {metrics.cacheHitRate}%</div>
      <div>Service Worker: {metrics.serviceWorkerStatus}</div>
      <div>Memory: {metrics.memoryUsage}MB</div>
      <div>Network Requests: {metrics.networkRequests}</div>
      <div style={{ 
        marginTop: '5px', 
        fontSize: '10px', 
        color: metrics.cacheHitRate > 50 ? '#00ff00' : '#ffaa00' 
      }}>
        {metrics.cacheHitRate > 50 ? '✅ Optimized' : '⚠️ Optimizing...'}
      </div>
    </div>
  );
};

export default PerformanceMonitor;
