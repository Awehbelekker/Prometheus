/**
 * Enhanced API Service for MASS Framework
 * Handles authentication, error handling, and production-ready features
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
}

interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
  expiresAt: number;
}

interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

class EnhancedApiService {
  private client: AxiosInstance;
  private config: ApiConfig;
  private tokens: AuthTokens | null = null;
  private refreshPromise: Promise<void> | null = null;

  constructor(config: Partial<ApiConfig> = {}) {
    // Prioritize explicit environment variable, then localhost for development
    const runtimeBase = (() => {
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
      // Dev fallback aligned with backend on 8000
      return 'http://localhost:8000';
    })();

    this.config = {
      baseURL: runtimeBase,
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadTokensFromStorage();
  }

  private setupInterceptors(): void {
    // Request interceptor for auth tokens
    this.client.interceptors.request.use(
      (config) => {
        if (this.tokens?.accessToken && !this.isTokenExpired()) {
          config.headers.Authorization = `Bearer ${this.tokens.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          if (this.tokens?.refreshToken) {
            try {
              await this.refreshToken();
              return this.client(originalRequest);
            } catch (refreshError) {
              this.clearTokens();
              window.location.href = '/login';
              return Promise.reject(refreshError);
            }
          } else {
            this.clearTokens();
            window.location.href = '/login';
          }
        }

        return Promise.reject(this.handleApiError(error));
      }
    );
  }

  private handleApiError(error: any): ApiError {
    if (error.response) {
      return {
        message: error.response.data?.detail || error.response.data?.message || 'API Error',
        status: error.response.status,
        code: error.response.data?.code,
        details: error.response.data,
      };
    } else if (error.request) {
      return {
        message: 'Network error - please check your connection',
        status: 0,
        code: 'NETWORK_ERROR',
      };
    } else {
      return {
        message: error.message || 'Unknown error occurred',
        status: 0,
        code: 'UNKNOWN_ERROR',
      };
    }
  }

  private isTokenExpired(): boolean {
    if (!this.tokens) return true;
    return Date.now() >= this.tokens.expiresAt;
  }

  private async refreshToken(): Promise<void> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
  const response = await axios.post(`${this.config.baseURL}/api/auth/refresh`, {
          refresh_token: this.tokens?.refreshToken,
        });

        const { access_token, refresh_token, expires_in } = response.data;
        this.setTokens({
          accessToken: access_token,
          refreshToken: refresh_token,
          expiresAt: Date.now() + expires_in * 1000,
        });
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  private loadTokensFromStorage(): void {
    try {
      const stored = localStorage.getItem('mass_auth_tokens');
      if (stored) {
        this.tokens = JSON.parse(stored);
      }
    } catch (error) {
      console.warn('Failed to load tokens from storage:', error);
      this.clearTokens();
    }
  }

  private saveTokensToStorage(): void {
    try {
      if (this.tokens) {
        localStorage.setItem('mass_auth_tokens', JSON.stringify(this.tokens));
      } else {
        localStorage.removeItem('mass_auth_tokens');
      }
    } catch (error) {
      console.warn('Failed to save tokens to storage:', error);
    }
  }

  public setTokens(tokens: AuthTokens): void {
    this.tokens = tokens;
    this.saveTokensToStorage();
  }

  public clearTokens(): void {
    this.tokens = null;
    this.saveTokensToStorage();
  }

  public isAuthenticated(): boolean {
    return this.tokens !== null && !this.isTokenExpired();
  }

  // Authentication methods
  public async login(username: string, password: string, tenantId?: string): Promise<any> {
  const response = await this.client.post('/api/auth/login', {
      username,
      password,
      tenant_id: tenantId,
    });

    const { access_token, refresh_token, expires_in } = response.data;
    this.setTokens({
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresAt: Date.now() + expires_in * 1000,
    });

    return response.data;
  }

  public async logout(): Promise<void> {
    if (this.tokens?.refreshToken) {
      try {
  await this.client.post('/api/auth/logout', {
          refresh_token: this.tokens.refreshToken,
        });
      } catch (error) {
        console.warn('Logout request failed:', error);
      }
    }
    this.clearTokens();
  }

  // AI Chat methods
  public async chat(message: string, conversationHistory: any[] = []): Promise<any> {
    const response = await this.client.post('/api/ai/chat', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  }

  public async generateCode(prompt: string, language: string = 'python'): Promise<any> {
    const response = await this.client.post('/api/ai/generate-code', {
      prompt,
      language,
      include_tests: true,
      include_documentation: true,
    });
    return response.data;
  }

  public async analyzeCode(code: string, language: string = 'python'): Promise<any> {
    const response = await this.client.post('/api/ai/analyze-code', {
      code,
      language,
    });
    return response.data;
  }

  // Workflow methods
  public async createWorkflow(name: string, description: string, steps: any[]): Promise<any> {
    const response = await this.client.post('/api/workflows', {
      name,
      description,
      steps,
    });
    return response.data;
  }

  public async getWorkflows(): Promise<any> {
    const response = await this.client.get('/api/workflows');
    return response.data;
  }

  public async executeWorkflow(workflowId: string, inputs: any = {}): Promise<any> {
    const response = await this.client.post(`/api/workflows/${workflowId}/execute`, inputs);
    return response.data;
  }

  // Agent collaboration methods
  public async startCollaboration(task: string, agents: string[] = []): Promise<any> {
    const response = await this.client.post('/api/collaboration/start', {
      task,
      agents,
    });
    return response.data;
  }

  public async getCollaborationStatus(sessionId: string): Promise<any> {
    const response = await this.client.get(`/api/collaboration/${sessionId}`);
    return response.data;
  }

  // System monitoring
  public async getSystemStats(): Promise<any> {
    const response = await this.client.get('/api/system/stats');
    return response.data;
  }

  public async getAIUsageStats(): Promise<any> {
    const response = await this.client.get('/api/ai/usage-stats');
    return response.data;
  }

  // Generic request method
  public async request<T = any>(config: AxiosRequestConfig): Promise<T> {
    const response = await this.client.request<T>(config);
    return response.data;
  }
}

// Create singleton instance
export const apiService = new EnhancedApiService();

// Export types for use in components
export type { ApiError, AuthTokens };
export default apiService;
