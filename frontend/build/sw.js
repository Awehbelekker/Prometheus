// PROMETHEUS Service Worker - Version 2.3.0 (2025-10-18)
// Phase 4 Enhancements Complete - FORCE CACHE CLEAR v2
const CACHE_NAME = 'prometheus-trading-v2.3.0-20251018-1200';
const CACHE_VERSION = '2.3.0';
const BUILD_DATE = '2025-10-18';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/favicon.svg'
  // Note: Bundle paths are dynamic and will be cached on-demand
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Caching essential files');
        // Filter out any non-http(s) URLs (defensive against extensions)
        const safeUrls = urlsToCache.filter((u) => {
          try {
            const p = new URL(u, self.location.origin);
            return p.protocol === 'http:' || p.protocol === 'https:';
          } catch (_) {
            return false;
          }
        });
        // Use Promise.allSettled to handle individual failures gracefully
        return Promise.allSettled(
          safeUrls.map(url => cache.add(url).catch(err => {
            console.warn(`Failed to cache ${url}:`, err);
            return null;
          }))
        );
      })
      .then(() => {
        console.log('✅ Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  // In localhost development, bypass SW handling entirely to avoid dev server conflicts
  try {
    const isLocalhost = self.location.hostname === 'localhost' || self.location.hostname === '127.0.0.1';
    if (isLocalhost) {
      return; // let the network handle it directly in dev
    }
  } catch (_) {}

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Ignore non-http(s) schemes (e.g., chrome-extension://) to prevent Cache.put errors
  let requestUrl;
  try {
    requestUrl = new URL(event.request.url);
    if (requestUrl.protocol !== 'http:' && requestUrl.protocol !== 'https:') {
      return;
    }
  } catch (_) {
    // If URL parsing fails, do not attempt to cache
    return;
  }

  // Skip WebSocket and API requests (CRITICAL: Preserve trading functionality)
  if (event.request.url.includes('/ws') ||
      event.request.url.includes('/api/') ||
      event.request.url.includes('localhost:8000') ||
      event.request.url.includes('localhost:8002') ||
      event.request.url.includes('prometheus-trader.com/api/')) {
    return;
  }

  // Only handle specific resource types to avoid no-op handlers
  const destination = event.request.destination;
  if (destination === 'document' ||
      destination === 'script' ||
      destination === 'style' ||
      destination === 'image' ||
      destination === 'font' ||
      destination === 'manifest') {

    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          // Return cached version if available
          if (response) {
            console.log('📦 Serving from cache:', event.request.url);
            return response;
          }

          // Otherwise fetch from network
          return fetch(event.request).then((response) => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response for caching
            const responseToCache = response.clone();

            // Cache the response asynchronously
            caches.open(CACHE_NAME)
              .then((cache) => {
                // Only cache same-origin http(s) GET requests
                try {
                  if ((requestUrl.protocol === 'http:' || requestUrl.protocol === 'https:') &&
                      event.request.method === 'GET') {
                    cache.put(event.request, responseToCache).catch((error) => {
                      console.warn('Cache put failed:', error);
                    });
                  }
                } catch (error) {
                  console.warn('Cache operation failed:', error);
                }
              })
              .catch((error) => {
                console.warn('Cache open failed:', error);
              });

            return response;
          }).catch((error) => {
            console.warn('Network fetch failed:', error);
            // Return a basic offline response for navigation requests
            if (destination === 'document') {
              return new Response('Offline - Please check your connection', {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'text/plain' }
              });
            }
            throw error;
          });
        })
    );
  }
});

// Push notification event
self.addEventListener('push', (event) => {
  console.log('📱 Push notification received:', event);
  
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'Prometheus Trading', body: event.data.text() || 'New trading update' };
    }
  }

  const options = {
    title: data.title || 'Prometheus Trading',
    body: data.body || 'You have a new trading notification',
    icon: '/logo192.png',
    badge: '/favicon.ico',
    tag: 'trading-notification',
    renotify: true,
    requireInteraction: false,
    actions: [
      {
        action: 'view',
        title: 'View Dashboard',
        icon: '/logo192.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ],
    data: {
      url: data.url || '/admin-dashboard',
      timestamp: Date.now()
    }
  };

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event);
  
  event.notification.close();

  if (event.action === 'view' || !event.action) {
    const urlToOpen = event.notification.data?.url || '/dashboard';
    
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then((clientList) => {
          // Check if the app is already open
          for (let client of clientList) {
            if (client.url.includes(urlToOpen) && 'focus' in client) {
              return client.focus();
            }
          }
          
          // Open new window if not already open
          if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
          }
        })
    );
  }
});

// Background sync for trade updates
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-trades') {
    event.waitUntil(
      syncTradeUpdates()
    );
  }
});

async function syncTradeUpdates() {
  try {
    // Sync trade data when connection is restored
    const response = await fetch('/api/trading/sync');
    const data = await response.json();
    
    // Show notification for important updates
    if (data.newTrades && data.newTrades.length > 0) {
      const profitableTrades = data.newTrades.filter(trade => trade.profit > 0);
      
      if (profitableTrades.length > 0) {
        await self.registration.showNotification('🚀 Profitable Trades!', {
          body: `${profitableTrades.length} profitable trades completed`,
          icon: '/logo192.png',
          tag: 'sync-trades'
        });
      }
    }
  } catch (error) {
    console.error('❌ Sync failed:', error);
  }
}

console.log('📱 Prometheus Trading Service Worker loaded');
