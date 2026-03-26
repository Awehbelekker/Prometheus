/**
 * 🎯 DUAL-TIER API SERVICE
 * Handles all API calls for the dual-tier permission system
 */

import { API_BASE_URL } from '../config/api';
import { getJsonWithRetry } from '../utils/network';


export interface UserPermissions {
  user_id: string;
  tier: 'paper_only' | 'live_approved' | 'admin';
  paper_trading_enabled: boolean;
  live_trading_enabled: boolean;
  allocated_funds: number;
  total_trades: number;
  total_profit_loss: number;
  achievements_count: number;
  current_level: number;
}

export interface AdminDashboard {
  total_users: number;
  paper_only_users: number;
  live_approved_users: number;
  total_allocated_funds: number;
  active_sessions: number;
  recent_allocations: any[];
}

export interface PaperTradingSession {
  session_id: string;
  session_type: '24_hour' | '48_hour' | '168_hour' | 'custom';
  starting_capital: number;
  current_value: number;
  duration_hours: number;
  status: 'not_started' | 'active' | 'paused' | 'completed' | 'cancelled';
  start_time?: string;
  end_time?: string;
  trades_count: number;
  profit_loss: number;
  return_percentage: number;
  time_remaining_hours?: number;
}

export interface UserDashboard {
  user_id: string;
  tier: string;
  paper_trading_enabled: boolean;
  live_trading_enabled: boolean;
  current_level: number;
  experience_points: number;
  total_achievements: number;
  active_sessions: PaperTradingSession[];
  recent_achievements: any[];
  leaderboard_rank?: number;
}

export interface Achievement {
  achievement_id: string;
  name: string;
  description: string;
  achievement_type: string;
  rarity: string;
  icon: string;
  points: number;
  earned: boolean;
}

class DualTierApiService {
  private baseUrl = API_BASE_URL;
  private adminId = 'admin_prometheus_001'; // In real app, get from auth
  private userId = 'user_demo_001'; // In real app, get from auth

  // Admin API Methods
  async getAdminDashboard(): Promise<AdminDashboard> {
    return await getJsonWithRetry(`${this.baseUrl}/api/admin/dashboard`, {
      headers: { 'X-Admin-ID': this.adminId }
    });
  }

  async getAllUsers(): Promise<UserPermissions[]> {
    return await getJsonWithRetry(`${this.baseUrl}/api/admin/users`, {
      headers: { 'X-Admin-ID': this.adminId }
    });
  }

  async allocateFunds(userId: string, amount: number, reason: string = ''): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/admin/allocate-funds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Admin-ID': this.adminId },
      body: JSON.stringify({ user_id: userId, amount, reason })
    });
  }

  async activateLiveTrading(userId: string, reason: string = ''): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/admin/activate-live-trading`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Admin-ID': this.adminId },
      body: JSON.stringify({ user_id: userId, reason })
    });
  }

  async getUserDetails(userId: string): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/admin/user/${userId}/details`, {
      headers: { 'X-Admin-ID': this.adminId }
    });
  }

  // User API Methods
  async getUserDashboard(): Promise<UserDashboard> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/dashboard`, {
      headers: { 'X-User-ID': this.userId }
    });
  }

  async createPaperSession(sessionType: string, startingCapital: number, customHours?: number): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/create-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-User-ID': this.userId },
      body: JSON.stringify({
        session_type: sessionType,
        starting_capital: startingCapital,
        custom_hours: customHours
      })
    });
  }

  async startSession(sessionId: string): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/start-session/${sessionId}`, {
      method: 'POST',
      headers: { 'X-User-ID': this.userId }
    });
  }

  async getSessionDetails(sessionId: string): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/session/${sessionId}`, {
      headers: { 'X-User-ID': this.userId }
    });
  }

  async getMarketData(): Promise<any> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/market-data`, {
      headers: { 'X-User-ID': this.userId }
    });
  }

  async getUserAchievements(): Promise<{ user_progress: any; achievements: Achievement[] }> {
    return await getJsonWithRetry(`${this.baseUrl}/api/user/achievements`, {
      headers: { 'X-User-ID': this.userId }
    });
  }

  // Utility Methods
  setUserId(userId: string) {
    this.userId = userId;
  }

  setAdminId(adminId: string) {
    this.adminId = adminId;
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  }

  formatPercentage(value: number): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  }

  calculateTimeRemaining(endTime: string): number {
    const end = new Date(endTime);
    const now = new Date();
    const diffMs = end.getTime() - now.getTime();
    return Math.max(0, diffMs / (1000 * 60 * 60)); // Convert to hours
  }
}

// Export singleton instance
export const dualTierApi = new DualTierApiService();
export default dualTierApi;
