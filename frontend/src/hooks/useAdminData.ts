/**
 * Custom hook for admin dashboard data fetching using React Query
 * Replaces multiple useState + useEffect patterns with optimized data fetching
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';
import { logger } from '../utils/logger';

interface AdminMetrics {
  totalUsers: number;
  activeTraders: number;
  totalAllocated: number;
  totalPortfolioValue: number;
  dailyPnL: number;
  systemUptime: number;
  pendingApprovals: number;
  activeSessions: number;
}

interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  status: 'pending' | 'approved' | 'active' | 'suspended';
  tier: 'paper_only' | 'live_approved' | 'admin';
  allocatedFunds: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
  joinDate: string;
  liveTrading: boolean;
  lastActivity: string;
}

const retryOpts = { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 } as const;

/**
 * Fetch admin dashboard metrics
 */
export const useAdminMetrics = (adminId: string) => {
  return useQuery<AdminMetrics>({
    queryKey: ['adminMetrics', adminId],
    queryFn: async () => {
      try {
        let dashboardData: any | null = null;
        try {
          dashboardData = await getJsonWithRetry(getApiUrl('/api/public/admin/dashboard'), {}, retryOpts);
        } catch {
          try {
            dashboardData = await getJsonWithRetry(getApiUrl('/api/admin/dashboard'), {
              headers: { 'X-Admin-ID': adminId }
            }, retryOpts);
          } catch {
            try {
              dashboardData = await getJsonWithRetry(getApiUrl('/api/admin/dashboard-summary'), {
                headers: { 'X-Admin-ID': adminId }
              }, retryOpts);
            } catch {
              dashboardData = null;
            }
          }
        }

        if (dashboardData) {
          return {
            totalUsers: dashboardData.total_users || 0,
            activeTraders: dashboardData.active_traders || 0,
            totalAllocated: dashboardData.total_allocated_funds || 0,
            totalPortfolioValue: dashboardData.total_portfolio_value || 0,
            dailyPnL: dashboardData.daily_pnl || 0,
            systemUptime: dashboardData.system_uptime || 0,
            pendingApprovals: dashboardData.pending_approvals || 0,
            activeSessions: dashboardData.active_sessions || 0
          } as AdminMetrics;
        }

        // Return default values if all endpoints fail
        return {
          totalUsers: 0,
          activeTraders: 0,
          totalAllocated: 0,
          totalPortfolioValue: 0,
          dailyPnL: 0,
          systemUptime: 0,
          pendingApprovals: 0,
          activeSessions: 0
        };
      } catch (error) {
        logger.error('Failed to fetch admin metrics', error, 'AdminData');
        throw error;
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // 1 minute
    retry: 3
  });
};

/**
 * Fetch admin users list
 */
export const useAdminUsers = (adminId: string) => {
  return useQuery<User[]>({
    queryKey: ['adminUsers', adminId],
    queryFn: async () => {
      try {
        let usersData: any | null = null;
        try {
          usersData = await getJsonWithRetry(getApiUrl('/api/public/admin/users'), {}, retryOpts);
        } catch {
          try {
            usersData = await getJsonWithRetry(getApiUrl('/api/admin/users'), {
              headers: { 'X-Admin-ID': adminId }
            }, retryOpts);
          } catch {
            usersData = null;
          }
        }

        if (usersData) {
          return Array.isArray(usersData) ? usersData : (usersData.users || []);
        }

        return [];
      } catch (error) {
        logger.error('Failed to fetch admin users', error, 'AdminData');
        throw error;
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // 1 minute
    retry: 3
  });
};

/**
 * Fetch live trading status
 */
export const useLiveTradingStatus = () => {
  return useQuery({
    queryKey: ['liveTradingStatus'],
    queryFn: async () => {
      try {
        let data: any | null = null;
        try {
          data = await getJsonWithRetry(getApiUrl('/api/live-trading/status'), {}, retryOpts);
        } catch {
          try {
            data = await getJsonWithRetry(getApiUrl('/api/trading/live-status'), {}, retryOpts);
          } catch {
            data = null;
          }
        }

        if (data) {
          return {
            isActive: data.isActive || false,
            activePositions: data.activePositions || 0,
            dailyPnL: data.dailyPnL || 0,
            winRate: data.winRate || 0,
            canActivate: data.canActivate ?? true
          };
        }

        return {
          isActive: false,
          activePositions: 0,
          dailyPnL: 0,
          winRate: 0,
          canActivate: true
        };
      } catch (error) {
        logger.error('Failed to fetch live trading status', error, 'AdminData');
        return {
          isActive: false,
          activePositions: 0,
          dailyPnL: 0,
          winRate: 0,
          canActivate: true
        };
      }
    },
    staleTime: 15000, // 15 seconds
    refetchInterval: 30000, // 30 seconds
    retry: 2
  });
};

/**
 * Fetch paper trading sessions
 */
export const usePaperTradingSessions = () => {
  return useQuery({
    queryKey: ['paperTradingSessions'],
    queryFn: async () => {
      try {
        let data: any | null = null;
        try {
          data = await getJsonWithRetry(getApiUrl('/api/public/user/sessions'), {}, retryOpts);
        } catch {
          try {
            data = await getJsonWithRetry(getApiUrl('/api/user/sessions'), {}, retryOpts);
          } catch {
            data = null;
          }
        }

        return data?.sessions || [];
      } catch (error) {
        logger.error('Failed to fetch paper trading sessions', error, 'AdminData');
        return [];
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // 1 minute
    retry: 2
  });
};

/**
 * Fetch audit logs
 */
export const useAuditLogs = (adminId: string, filters?: {
  actionType?: string;
  dateRange?: string;
  userId?: string;
}) => {
  return useQuery({
    queryKey: ['auditLogs', adminId, filters],
    queryFn: async () => {
      try {
        const response = await getJsonWithRetry(getApiUrl('/api/admin/audit-logs'), {
          headers: { 'X-Admin-ID': adminId }
        }, retryOpts);
        return response?.logs || [];
      } catch (error) {
        logger.error('Failed to fetch audit logs', error, 'AdminData');
        return [];
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // 1 minute
    retry: 2
  });
};

/**
 * Fetch invitations
 */
export const useInvitations = (adminId: string) => {
  return useQuery({
    queryKey: ['invitations', adminId],
    queryFn: async () => {
      try {
        const response = await getJsonWithRetry(getApiUrl('/api/admin/invitations'), {
          headers: { 'X-Admin-ID': adminId }
        }, retryOpts);
        return response?.invitations || [];
      } catch (error) {
        logger.error('Failed to fetch invitations', error, 'AdminData');
        return [];
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // 1 minute
    retry: 2
  });
};

/**
 * Mutation for fund allocation
 */
export const useAllocateFunds = (adminId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      userId: string;
      amount: number;
      reason: string;
    }) => {
      return await getJsonWithRetry(getApiUrl('/api/admin/allocate-funds'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-ID': adminId
        },
        body: JSON.stringify({
          user_id: data.userId,
          amount: data.amount,
          reason: data.reason
        })
      }, retryOpts);
    },
    onSuccess: () => {
      // Invalidate and refetch admin data
      queryClient.invalidateQueries({ queryKey: ['adminMetrics', adminId] });
      queryClient.invalidateQueries({ queryKey: ['adminUsers', adminId] });
      logger.info('Funds allocated successfully', undefined, 'AdminData');
    },
    onError: (error) => {
      logger.error('Failed to allocate funds', error, 'AdminData');
    }
  });
};

/**
 * Mutation for sending invitations
 */
export const useSendInvitation = (adminId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      email: string;
      name: string;
      role: string;
      tier: string;
      initialBalance: number;
      inviteMessage: string;
    }) => {
      const token = localStorage.getItem('authToken');
      const response = await fetch(getApiUrl('/api/admin/invite-user'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error('Failed to send invitation');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invitations', adminId] });
      logger.info('Invitation sent successfully', undefined, 'AdminData');
    },
    onError: (error) => {
      logger.error('Failed to send invitation', error, 'AdminData');
    }
  });
};

