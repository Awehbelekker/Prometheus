// PWA utilities for Prometheus Trading Platform

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export class PWAManager {
  private deferredPrompt: BeforeInstallPromptEvent | null = null;
  private registration: ServiceWorkerRegistration | null = null;

  constructor() {
    this.initServiceWorker();
    this.setupInstallPrompt();
    this.requestNotificationPermission();
  }

  // Register service worker
  private async initServiceWorker() {
    // Skip SW in local development to avoid dev server conflicts and extension cache errors
    const isLocalhost = typeof window !== 'undefined' && (
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'
    );
    if (isLocalhost) {
      console.log('⚠️ Skipping Service Worker registration on localhost');
      return;
    }

    // Check if PWA is enabled in environment
    const isPWAEnabled = process.env.REACT_APP_PWA_ENABLED !== 'false';
    if (!isPWAEnabled) {
      console.log('⚠️ PWA disabled in environment configuration');
      return;
    }

    if ('serviceWorker' in navigator) {
      try {
        console.log('🔧 Registering service worker...');
        this.registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });

        console.log('✅ Service Worker registered successfully:', this.registration);

        // Listen for updates
        this.registration.addEventListener('updatefound', () => {
          console.log('🔄 Service Worker update found');
          const newWorker = this.registration?.installing;
          
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                console.log('📱 New content available, please refresh');
                this.showUpdateNotification();
              }
            });
          }
        });

        // Enable background sync
        if ('sync' in window.ServiceWorkerRegistration.prototype) {
          console.log('🔄 Background sync supported');
        }

      } catch (error) {
        console.error('❌ Service Worker registration failed:', error);
      }
    } else {
      console.warn('⚠️ Service Worker not supported');
    }
  }

  // Setup install prompt
  private setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e: Event) => {
      console.log('📱 Install prompt available');
      e.preventDefault();
      this.deferredPrompt = e as BeforeInstallPromptEvent;
      
      // Show custom install button
      this.showInstallBanner();
    });

    // Track when app is installed
    window.addEventListener('appinstalled', () => {
      console.log('✅ App installed successfully');
      this.deferredPrompt = null;
      this.hideInstallBanner();
      
      // Send analytics event
      this.trackInstallEvent();
    });
  }

  // Request notification permission
  private async requestNotificationPermission() {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      console.log('🔔 Notification permission:', permission);
      
      if (permission === 'granted') {
        console.log('✅ Notifications enabled');
        this.setupPushSubscription();
      }
    } else {
      console.warn('⚠️ Notifications not supported');
    }
  }

  // Setup push notifications
  private async setupPushSubscription() {
    if (!this.registration) return;

    try {
      // For now, skip push subscription setup until VAPID keys are configured
      console.log('📡 Push notifications setup (VAPID keys needed)');
      
      // TODO: Replace with actual VAPID key implementation
      /*
      const subscription = await this.registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(
          'YOUR_VAPID_PUBLIC_KEY_HERE'
        )
      });

      console.log('📡 Push subscription created:', subscription);
      await this.sendSubscriptionToServer(subscription);
      */
      
    } catch (error) {
      console.error('❌ Push subscription failed:', error);
    }
  }

  // Convert VAPID key
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Send subscription to server
  private async sendSubscriptionToServer(subscription: PushSubscription) {
    try {
      const response = await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(subscription)
      });

      if (response.ok) {
        console.log('✅ Push subscription sent to server');
      }
    } catch (error) {
      console.error('❌ Failed to send subscription to server:', error);
    }
  }

  // Show install banner
  private showInstallBanner() {
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(45deg, #00d4ff, #ff6b35);
        color: white;
        padding: 16px;
        text-align: center;
        z-index: 10000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      ">
        <div style="max-width: 600px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
          <div>
            <strong>📱 Install Prometheus Trading</strong>
            <div style="font-size: 14px; opacity: 0.9;">Get faster access and real-time notifications</div>
          </div>
          <div style="display: flex; gap: 12px;">
            <button id="pwa-install-btn" style="
              background: rgba(255,255,255,0.2);
              border: 1px solid rgba(255,255,255,0.5);
              color: white;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              font-weight: bold;
            ">Install App</button>
            <button id="pwa-dismiss-btn" style="
              background: transparent;
              border: 1px solid rgba(255,255,255,0.5);
              color: white;
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
            ">Not Now</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(banner);

    // Add event listeners
    document.getElementById('pwa-install-btn')?.addEventListener('click', () => {
      this.showInstallPrompt();
    });

    document.getElementById('pwa-dismiss-btn')?.addEventListener('click', () => {
      this.hideInstallBanner();
    });
  }

  // Show install prompt
  public async showInstallPrompt() {
    if (!this.deferredPrompt) return;

    try {
      await this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      
      console.log('📱 Install prompt result:', outcome);
      
      if (outcome === 'accepted') {
        console.log('✅ User accepted the install prompt');
      } else {
        console.log('❌ User dismissed the install prompt');
      }
      
      this.deferredPrompt = null;
      this.hideInstallBanner();
      
    } catch (error) {
      console.error('❌ Install prompt failed:', error);
    }
  }

  // Hide install banner
  private hideInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.remove();
    }
  }

  // Show update notification
  private showUpdateNotification() {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🔄 App Update Available', {
        body: 'Please refresh the page to get the latest features',
        icon: '/logo192.png',
        tag: 'app-update',
        requireInteraction: true
      });
    }
  }

  // Track install event
  private trackInstallEvent() {
    // Send analytics event
    console.log('📊 App install tracked');
    
    // You can integrate with analytics here
    try {
      if (typeof (window as any).gtag !== 'undefined') {
        (window as any).gtag('event', 'pwa_install', {
          event_category: 'engagement',
          event_label: 'app_install'
        });
      }
    } catch (error) {
      console.log('Analytics not available');
    }
  }

  // Send notification
  public async sendNotification(title: string, options: NotificationOptions = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(title, {
        icon: '/logo192.png',
        badge: '/favicon.ico',
        tag: 'trading-update',
        ...options
      });

      // Auto-close after 10 seconds
      setTimeout(() => {
        notification.close();
      }, 10000);

      return notification;
    }
  }

  // Check if app is installed
  public isInstalled(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }

  // Get installation status
  public getInstallationStatus() {
    return {
      isInstalled: this.isInstalled(),
      canInstall: !!this.deferredPrompt,
      notificationsEnabled: 'Notification' in window && Notification.permission === 'granted',
      serviceWorkerSupported: 'serviceWorker' in navigator
    };
  }
}

// Create global PWA manager instance
export const pwaManager = new PWAManager();

// Expose for debugging
if (typeof window !== 'undefined') {
  (window as any).pwaManager = pwaManager;
}
