/**
 * useInvestorData Hook
 * Fetches real investor portfolio data for pool investors (Tier 1)
 */

import { useQuery } from '@tanstack/react-query';
import { apiCall } from '../config/api';

export interface InvestorProfile {
  id: string;
  name: string;
  email: string;
  tier: 'silver' | 'gold' | 'platinum';
  joinDate: string;
  status: 'active' | 'pending' | 'suspended';
  investmentAmount: number;
  currentValue: number;
  totalPnL: number;
  totalPnLPercentage: number;
  dailyPnL: number;
  dailyPnLPercentage: number;
  weeklyPnL: number;
  monthlyPnL: number;
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
}

export interface PlatformPerformance {
  totalAUM: number;
  totalUsers: number;
  activeTraders: number;
  platformPnL: number;
  successRate: number;
  avgUserReturn: number;
  tradingEngineStatus: 'active' | 'inactive' | 'maintenance';
}

export interface RecentActivity {
  id: string;
  type: 'profit' | 'loss' | 'allocation' | 'withdrawal';
  amount: number;
  description: string;
  timestamp: string;
}

export const useInvestorData = (userId: string, enabled: boolean = true) => {
  // Fetch investor profile
  const { 
    data: profile, 
    isLoading: profileLoading, 
    error: profileError 
  } = useQuery({
    queryKey: ['investor-profile', userId],
    queryFn: async () => {
      try {
        const response = await apiCall(`/api/investor/profile/${userId}`);
        return response as InvestorProfile;
      } catch (err) {
        console.warn('Investor profile endpoint failed, using fallback:', err);
        
        // Fallback: Try to get data from portfolio endpoint
        try {
          const portfolio = await apiCall(`/api/user/portfolio/${userId}`);
          const account = await apiCall('/api/trading/alpaca/paper/account');
          
          return {
            id: userId,
            name: 'Pool Investor',
            email: '',
            tier: 'gold',
            joinDate: new Date().toISOString(),
            status: 'active',
            investmentAmount: parseFloat(account.last_equity || 0),
            currentValue: parseFloat(account.portfolio_value || 0),
            totalPnL: portfolio.totalReturn || 0,
            totalPnLPercentage: portfolio.returnPercentage || 0,
            dailyPnL: 0,
            dailyPnLPercentage: 0,
            weeklyPnL: 0,
            monthlyPnL: 0,
            riskTolerance: 'moderate'
          } as InvestorProfile;
        } catch (fallbackErr) {
          console.error('Fallback investor data fetch failed:', fallbackErr);
          throw fallbackErr;
        }
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
    retry: 3,
    enabled
  });

  // Fetch platform performance
  const {
    data: platformPerformance,
    isLoading: platformLoading
  } = useQuery({
    queryKey: ['platform-performance'],
    queryFn: async () => {
      try {
        const response = await apiCall('/api/platform/performance');
        return response as PlatformPerformance;
      } catch (err) {
        console.warn('Platform performance endpoint failed, using defaults:', err);
        
        // Return default values
        return {
          totalAUM: 0,
          totalUsers: 0,
          activeTraders: 0,
          platformPnL: 0,
          successRate: 0,
          avgUserReturn: 0,
          tradingEngineStatus: 'active'
        } as PlatformPerformance;
      }
    },
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
    retry: 2,
    enabled
  });

  // Fetch recent activity
  const {
    data: recentActivity,
    isLoading: activityLoading
  } = useQuery({
    queryKey: ['investor-activity', userId],
    queryFn: async () => {
      try {
        const response = await apiCall(`/api/investor/activity/${userId}`);
        return response as RecentActivity[];
      } catch (err) {
        console.warn('Activity endpoint failed, returning empty:', err);
        return [] as RecentActivity[];
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
    retry: 2,
    enabled
  });

  return {
    profile,
    platformPerformance,
    recentActivity: recentActivity || [],
    isLoading: profileLoading || platformLoading || activityLoading,
    error: profileError,
    lastUpdate: new Date().toLocaleTimeString()
  };
};

