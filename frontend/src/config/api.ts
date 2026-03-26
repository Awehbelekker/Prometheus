// Generic API call helper with automatic authentication
export async function apiCall(endpoint: string, options: RequestInit = {}): Promise<any> {
  const url = getApiUrl(endpoint);

  // Get authentication token from localStorage
  const token = (() => {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  })();

  // Prepare headers with authentication
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// API call helper for text responses
export async function apiCallText(endpoint: string, options: RequestInit = {}): Promise<string> {
  const url = getApiUrl(endpoint);

  // Get authentication token from localStorage
  const token = (() => {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  })();

  // Prepare headers with authentication
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

// API call helper for blob responses (files, downloads)
export async function apiCallBlob(endpoint: string, options: RequestInit = {}): Promise<Blob> {
  const url = getApiUrl(endpoint);

  // Get authentication token from localStorage
  const token = (() => {
    try {
      return localStorage.getItem('authToken');
    } catch {
      return null;
    }
  })();

  // Prepare headers with authentication
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }
  return response.blob();
}
// API Configuration

// Use environment variable for API base URL, always prefer explicit config over origin
export const API_BASE_URL = (() => {
  // Always prioritize explicit environment variable
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  // For development, always use localhost:8000 regardless of window.location
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  // Only for production builds served by backend, use current origin
  if (typeof window !== 'undefined' && window.location && window.location.origin && 
      window.location.origin.includes('localhost:8000')) {
    return window.location.origin;
  }
  // Dev fallback: backend runs on 8000 in this setup
  return 'http://localhost:8000';
})();

export const WS_BASE_URL = (() => {
  // Use the same base as API_BASE_URL for consistency
  const base = API_BASE_URL;
  if (base.startsWith('https://')) return base.replace('https://', 'wss://');
  if (base.startsWith('http://')) return base.replace('http://', 'ws://');
  // Fallback - updated to match current backend port
  return 'ws://localhost:8000';
})();

export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  VALIDATE_INVITATION: '/api/auth/validate-invitation',
  LOGOUT: '/api/auth/logout',
  ME: '/api/auth/me',
  
  // Trading endpoints
  START_TRIAL: '/api/trading/start-trial',
  START_TRADING: '/api/trading/start',
  LIVE_TRADING_STATUS: '/api/live-trading/status',
  LIVE_TRADING_START: '/api/live-trading/start',
  LIVE_TRADING_START_ENGINE: '/api/live-trading/start-engine',
  
  // Orders
  TRADING_ORDERS: '/api/trading/orders',
  
  // Broker endpoints
  BROKER_CREDENTIALS: '/api/broker-credentials',
  
  // Workflow endpoints
  WORKFLOWS: '/api/workflows',
  WORKFLOW_TEMPLATES: '/api/workflow-templates',
  EXECUTE_WORKFLOW: (id: string) => `/api/workflows/${id}/execute`,
  CANCEL_WORKFLOW: (id: string) => `/api/workflows/${id}/cancel`,
  
  // System endpoints
  STATUS: '/health',
  AGENTS: '/agents/',
  PERFORMANCE_METRICS: '/api/system/performance-metrics',
  SYSTEM_PERFORMANCE: '/api/system/performance',
  AGENT_ACTIVATE: (agentId: string) => `/api/agents/${agentId}/activate`,
  AGENT_DEACTIVATE: (agentId: string) => `/api/agents/${agentId}/deactivate`,
  
  // User endpoints
  USER_DASHBOARD: (userId: string) => `/api/user/${userId}/dashboard`,
  FEATURE_FLAGS: '/api/features/flags',
  PERSONA_APPLY: '/api/strategy/persona/apply',
  PERSONA_ACTIVE: '/api/strategy/persona/active',
  RISK_PROFILE: '/api/risk/profile',
  AUDIT_RECENT: '/api/audit/recent',
  AUDIT_EXPORT: '/api/audit/export',
  
  // Real Alpaca Trading endpoints (replacing demo data)
  ALPACA_PAPER_ACCOUNT: '/api/trading/alpaca/paper/account',
  ALPACA_PAPER_PORTFOLIO: '/api/trading/alpaca/portfolio/history',
  ALPACA_PAPER_POSITIONS: '/api/trading/alpaca/paper/positions',
  ALPACA_PAPER_ORDERS: '/api/trading/alpaca/paper/orders',
  ALPACA_LIVE_ACCOUNT: '/api/trading/alpaca/live/account',
  ALPACA_LIVE_PORTFOLIO: '/api/trading/alpaca/live/portfolio',
  ALPACA_LIVE_POSITIONS: '/api/trading/alpaca/live/positions',
  ALPACA_LIVE_ORDERS: '/api/trading/alpaca/live/orders',
  
  // WebSocket endpoints
  DASHBOARD_WS: '/ws/dashboard-client'
};

export const getApiUrl = (endpoint: string) => `${API_BASE_URL}${endpoint}`;
export const getWsUrl = (endpoint: string) => `${WS_BASE_URL}${endpoint}`;
export function getAuthedWsUrl(endpoint: string, token?: string){
  if(!token) return getWsUrl(endpoint);
  const base = getWsUrl(endpoint);
  const sep = base.includes('?')? '&':'?';
  return `${base}${sep}token=${encodeURIComponent(token)}`;
}