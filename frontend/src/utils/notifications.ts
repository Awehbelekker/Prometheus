/**
 * 🔔 BROWSER NOTIFICATIONS UTILITY
 * 
 * Handles browser notifications for important trading events:
 * - High-confidence opportunities
 * - Agent status changes
 * - Critical system alerts
 */

export type NotificationPermission = 'granted' | 'denied' | 'default';

/**
 * Request notification permission from the user
 */
export const requestNotificationPermission = async (): Promise<NotificationPermission> => {
  if (!('Notification' in window)) {
    console.warn('This browser does not support notifications');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return 'granted';
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission as NotificationPermission;
  }

  return Notification.permission as NotificationPermission;
};

/**
 * Check if notifications are supported and enabled
 */
export const areNotificationsEnabled = (): boolean => {
  return 'Notification' in window && Notification.permission === 'granted';
};

/**
 * Show a browser notification
 */
export const showNotification = (title: string, options?: NotificationOptions): void => {
  if (!areNotificationsEnabled()) {
    console.warn('Notifications are not enabled');
    return;
  }

  try {
    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options
    });
  } catch (error) {
    console.error('Failed to show notification:', error);
  }
};

/**
 * Show notification for high-confidence opportunity
 */
export const notifyHighConfidenceOpportunity = (opportunity: {
  symbol: string;
  type: string;
  confidence: number;
  potentialProfit: number;
  description: string;
}): void => {
  if (!areNotificationsEnabled()) return;

  const title = `🎯 High-Confidence Opportunity: ${opportunity.symbol}`;
  const body = `${opportunity.type.toUpperCase()} - ${opportunity.confidence}% confidence\n` +
               `Potential Profit: $${opportunity.potentialProfit.toLocaleString()}\n` +
               `${opportunity.description}`;

  showNotification(title, {
    body,
    tag: `opportunity-${opportunity.symbol}`,
    requireInteraction: true,
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Show notification for agent status change
 */
export const notifyAgentStatusChange = (agentName: string, status: string, message?: string): void => {
  if (!areNotificationsEnabled()) return;

  const statusEmoji = status === 'active' ? '✅' : status === 'error' ? '❌' : '⚠️';
  const title = `${statusEmoji} Agent Status: ${agentName}`;
  const body = message || `Agent is now ${status.toUpperCase()}`;

  showNotification(title, {
    body,
    tag: `agent-${agentName}`,
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Show notification for critical system alert
 */
export const notifyCriticalAlert = (message: string, details?: string): void => {
  if (!areNotificationsEnabled()) return;

  const title = `🚨 PROMETHEUS Alert`;
  const body = details ? `${message}\n${details}` : message;

  showNotification(title, {
    body,
    tag: 'critical-alert',
    requireInteraction: true,
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Show notification for trading session event
 */
export const notifyTradingSession = (event: 'started' | 'stopped' | 'paused', details?: string): void => {
  if (!areNotificationsEnabled()) return;

  const eventEmoji = event === 'started' ? '🚀' : event === 'stopped' ? '🛑' : '⏸️';
  const title = `${eventEmoji} Trading Session ${event.toUpperCase()}`;
  const body = details || `Trading session has been ${event}`;

  showNotification(title, {
    body,
    tag: 'trading-session',
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Show notification for profit milestone
 */
export const notifyProfitMilestone = (amount: number, period: string): void => {
  if (!areNotificationsEnabled()) return;

  const title = `💰 Profit Milestone Reached!`;
  const body = `You've earned $${amount.toLocaleString()} in ${period}!`;

  showNotification(title, {
    body,
    tag: 'profit-milestone',
    requireInteraction: true,
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Show notification for risk alert
 */
export const notifyRiskAlert = (level: 'low' | 'medium' | 'high' | 'critical', message: string): void => {
  if (!areNotificationsEnabled()) return;

  const levelEmoji = level === 'critical' ? '🚨' : level === 'high' ? '⚠️' : level === 'medium' ? '⚡' : 'ℹ️';
  const title = `${levelEmoji} Risk Alert: ${level.toUpperCase()}`;

  showNotification(title, {
    body: message,
    tag: `risk-alert-${level}`,
    requireInteraction: level === 'critical' || level === 'high',
    icon: '/favicon.ico',
    badge: '/favicon.ico'
  });
};

/**
 * Play notification sound (optional)
 */
export const playNotificationSound = (soundType: 'success' | 'warning' | 'error' = 'success'): void => {
  try {
    const audio = new Audio();
    
    // Use different frequencies for different sound types
    const context = new AudioContext();
    const oscillator = context.createOscillator();
    const gainNode = context.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(context.destination);
    
    // Set frequency based on sound type
    switch (soundType) {
      case 'success':
        oscillator.frequency.value = 800;
        break;
      case 'warning':
        oscillator.frequency.value = 600;
        break;
      case 'error':
        oscillator.frequency.value = 400;
        break;
    }
    
    gainNode.gain.value = 0.1;
    oscillator.start(context.currentTime);
    oscillator.stop(context.currentTime + 0.1);
  } catch (error) {
    console.error('Failed to play notification sound:', error);
  }
};

/**
 * Store notification preferences in localStorage
 */
export const setNotificationPreferences = (preferences: {
  enabled: boolean;
  opportunities: boolean;
  agents: boolean;
  alerts: boolean;
  sound: boolean;
  minConfidence?: number;
}): void => {
  localStorage.setItem('notification_preferences', JSON.stringify(preferences));
};

/**
 * Get notification preferences from localStorage
 */
export const getNotificationPreferences = (): {
  enabled: boolean;
  opportunities: boolean;
  agents: boolean;
  alerts: boolean;
  sound: boolean;
  minConfidence: number;
} => {
  const stored = localStorage.getItem('notification_preferences');
  
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (error) {
      console.error('Failed to parse notification preferences:', error);
    }
  }
  
  // Default preferences
  return {
    enabled: true,
    opportunities: true,
    agents: true,
    alerts: true,
    sound: true,
    minConfidence: 80
  };
};

/**
 * Check if notification should be shown based on preferences
 */
export const shouldNotify = (type: 'opportunity' | 'agent' | 'alert', confidence?: number): boolean => {
  const prefs = getNotificationPreferences();
  
  if (!prefs.enabled) return false;
  
  switch (type) {
    case 'opportunity':
      if (!prefs.opportunities) return false;
      if (confidence !== undefined && confidence < prefs.minConfidence) return false;
      return true;
    case 'agent':
      return prefs.agents;
    case 'alert':
      return prefs.alerts;
    default:
      return false;
  }
};

