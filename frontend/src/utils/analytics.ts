/**
 * Analytics Tracking Utilities
 * Track user interactions and events for analytics
 */

export interface AnalyticsEvent {
  category: string;
  action: string;
  label?: string;
  value?: number;
  userId?: string;
}

export interface PageViewEvent {
  path: string;
  title: string;
  userId?: string;
}

export interface TradeEvent {
  symbol: string;
  action: 'buy' | 'sell';
  quantity: number;
  price: number;
  userId: string;
}

/**
 * Track custom event
 */
export const trackEvent = (event: AnalyticsEvent): void => {
  const { category, action, label, value, userId } = event;

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics] Event:', { category, action, label, value, userId });
  }

  // Send to analytics service (Google Analytics, Mixpanel, etc.)
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
      user_id: userId
    });
  }

  // Send to backend analytics endpoint
  try {
    fetch('/api/analytics/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, action, label, value, userId, timestamp: new Date().toISOString() })
    }).catch(err => console.warn('[Analytics] Failed to send event:', err));
  } catch (err) {
    console.warn('[Analytics] Failed to send event:', err);
  }
};

/**
 * Track page view
 */
export const trackPageView = (event: PageViewEvent): void => {
  const { path, title, userId } = event;

  if (process.env.NODE_ENV === 'development') {
    console.log('[Analytics] Page View:', { path, title, userId });
  }

  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: path,
      page_title: title,
      user_id: userId
    });
  }

  try {
    fetch('/api/analytics/pageview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path, title, userId, timestamp: new Date().toISOString() })
    }).catch(err => console.warn('[Analytics] Failed to send page view:', err));
  } catch (err) {
    console.warn('[Analytics] Failed to send page view:', err);
  }
};

/**
 * Track trade event
 */
export const trackTrade = (event: TradeEvent): void => {
  const { symbol, action, quantity, price, userId } = event;

  trackEvent({
    category: 'Trading',
    action: `trade_${action}`,
    label: symbol,
    value: quantity * price,
    userId
  });

  // Send detailed trade data to backend
  try {
    fetch('/api/analytics/trade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, action, quantity, price, userId, timestamp: new Date().toISOString() })
    }).catch(err => console.warn('[Analytics] Failed to send trade event:', err));
  } catch (err) {
    console.warn('[Analytics] Failed to send trade event:', err);
  }
};

/**
 * Track button click
 */
export const trackButtonClick = (buttonName: string, userId?: string): void => {
  trackEvent({
    category: 'User Interaction',
    action: 'button_click',
    label: buttonName,
    userId
  });
};

/**
 * Track feature usage
 */
export const trackFeatureUsage = (featureName: string, userId?: string): void => {
  trackEvent({
    category: 'Feature Usage',
    action: 'feature_used',
    label: featureName,
    userId
  });
};

/**
 * Track error
 */
export const trackError = (errorMessage: string, errorStack?: string, userId?: string): void => {
  trackEvent({
    category: 'Error',
    action: 'error_occurred',
    label: errorMessage,
    userId
  });

  // Send detailed error to backend
  try {
    fetch('/api/analytics/error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: errorMessage, 
        stack: errorStack, 
        userId, 
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    }).catch(err => console.warn('[Analytics] Failed to send error:', err));
  } catch (err) {
    console.warn('[Analytics] Failed to send error:', err);
  }
};

/**
 * Track user session start
 */
export const trackSessionStart = (userId: string): void => {
  trackEvent({
    category: 'Session',
    action: 'session_start',
    userId
  });
};

/**
 * Track user session end
 */
export const trackSessionEnd = (userId: string, duration: number): void => {
  trackEvent({
    category: 'Session',
    action: 'session_end',
    value: duration,
    userId
  });
};

/**
 * Track achievement unlock
 */
export const trackAchievementUnlock = (achievementName: string, userId: string): void => {
  trackEvent({
    category: 'Gamification',
    action: 'achievement_unlock',
    label: achievementName,
    userId
  });
};

/**
 * Track level up
 */
export const trackLevelUp = (newLevel: number, userId: string): void => {
  trackEvent({
    category: 'Gamification',
    action: 'level_up',
    value: newLevel,
    userId
  });
};

/**
 * Track search
 */
export const trackSearch = (searchQuery: string, userId?: string): void => {
  trackEvent({
    category: 'Search',
    action: 'search_performed',
    label: searchQuery,
    userId
  });
};

/**
 * Track filter usage
 */
export const trackFilter = (filterName: string, filterValue: string, userId?: string): void => {
  trackEvent({
    category: 'Filter',
    action: 'filter_applied',
    label: `${filterName}: ${filterValue}`,
    userId
  });
};

/**
 * Track modal open
 */
export const trackModalOpen = (modalName: string, userId?: string): void => {
  trackEvent({
    category: 'Modal',
    action: 'modal_open',
    label: modalName,
    userId
  });
};

/**
 * Track modal close
 */
export const trackModalClose = (modalName: string, userId?: string): void => {
  trackEvent({
    category: 'Modal',
    action: 'modal_close',
    label: modalName,
    userId
  });
};

/**
 * Track form submission
 */
export const trackFormSubmit = (formName: string, success: boolean, userId?: string): void => {
  trackEvent({
    category: 'Form',
    action: success ? 'form_submit_success' : 'form_submit_error',
    label: formName,
    userId
  });
};

/**
 * Track API call performance
 */
export const trackApiPerformance = (endpoint: string, duration: number, success: boolean): void => {
  trackEvent({
    category: 'API Performance',
    action: success ? 'api_success' : 'api_error',
    label: endpoint,
    value: Math.round(duration)
  });
};

export default {
  trackEvent,
  trackPageView,
  trackTrade,
  trackButtonClick,
  trackFeatureUsage,
  trackError,
  trackSessionStart,
  trackSessionEnd,
  trackAchievementUnlock,
  trackLevelUp,
  trackSearch,
  trackFilter,
  trackModalOpen,
  trackModalClose,
  trackFormSubmit,
  trackApiPerformance
};

