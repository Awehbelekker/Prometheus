/**
 * API Service for Prometheus Trading Platform
 * Connects frontend to the unified production backend
 */

import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';


export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  refresh_token?: string;
}

export interface UserInfo {
  user: {
    user_id: string;
    tier: string;
    email: string;
    role_raw?: string;
  };
  access_level: string;
  features: Record<string, boolean>;
}

export interface AlpacaAccountStatus {
  configured: boolean;
  mode: 'paper' | 'live';
  account?: {
    account_number: string;
    status: string;
    currency: string;
    buying_power: string;
    cash: string;
    portfolio_value: string;
    equity: string;
    pattern_day_trader: boolean;
    trading_blocked: boolean;
  };
  error?: string;
  note?: string;
}

class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('authToken');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = getApiUrl(endpoint);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      // Centralized JSON fetch with retry and timeout
      return await getJsonWithRetry<T>(url, {
        ...options,
        headers,
      }, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 8000 });
    } catch (error: any) {
      // Handle 403 Forbidden errors (admin access required)
      if (error.message && error.message.includes('HTTP 403')) {
        console.warn('🚫 Admin access required - redirecting to user dashboard');

        // Show user-friendly message
        if (typeof window !== 'undefined') {
          alert('This feature is only available to administrators.');

          // Redirect to user dashboard if not already there
          if (window.location.pathname !== '/dashboard') {
            window.location.href = '/dashboard';
          }
        }
      }

      // Re-throw the error for the caller to handle
      throw error;
    }
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    this.token = response.access_token;
    localStorage.setItem('authToken', this.token);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/api/auth/logout', {
        method: 'POST',
      });
    } finally {
      this.token = null;
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    }
  }

  async getCurrentUser(): Promise<UserInfo> {
    return this.request<UserInfo>('/api/auth/me');
  }

  async getAlpacaStatus(): Promise<AlpacaAccountStatus> {
    return this.request<AlpacaAccountStatus>('/api/broker/alpaca/account');
  }

  async getHealth(): Promise<any> {
    return this.request('/health');
  }

  async getFeatureAvailability(): Promise<any> {
    return this.request('/api/features/availability');
  }

  async start48HourDemo(config: any): Promise<any> {
    return this.request('/api/trading/start-48hour-demo', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async getQuantumOptimization(): Promise<any> {
    return this.request('/api/quantum/portfolio/optimize', {
      method: 'POST',
    });
  }

  async getAIConsciousnessStatus(): Promise<any> {
    return this.request('/api/ai/consciousness/status');
  }

  // Trading endpoints
  async placeOrder(orderData: {
    symbol: string;
    qty: number;
    side: 'buy' | 'sell';
    type: 'market' | 'limit' | 'stop' | 'stop_limit';
    limit_price?: number;
    stop_price?: number;
    time_in_force?: string;
  }): Promise<any> {
    return this.request('/api/trading/orders/place', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  async getOrders(status?: string, limit: number = 50): Promise<any> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', limit.toString());

    return this.request(`/api/trading/orders?${params.toString()}`);
  }

  async getPositions(): Promise<any> {
    return this.request('/api/trading/positions');
  }

  async applyPersona(persona: string): Promise<any> {
    return this.request('/api/strategy/persona/apply', {
      method: 'POST',
      body: JSON.stringify({ persona }),
    });
  }

  async getActivePersona(): Promise<any> {
    return this.request('/api/strategy/persona/active');
  }

  // Helper method to check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Method to set token if obtained elsewhere
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('authToken', token);
  }
}

export const apiService = new ApiService();

// Export trading functions for easier use
export const placeOrder = (orderData: {
  symbol: string;
  qty: number;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  limit_price?: number;
  stop_price?: number;
  time_in_force?: string;
}) => apiService.placeOrder(orderData);

export const getOrders = (status?: string, limit: number = 50) => apiService.getOrders(status, limit);

export const getPositions = () => apiService.getPositions();

export const applyPersona = (persona: string) => apiService.applyPersona(persona);

export const getActivePersona = () => apiService.getActivePersona();

export default apiService;
