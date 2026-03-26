/**
 * useLeaderboard Hook
 * Fetches gamification leaderboard data from backend
 */

import { useQuery } from '@tanstack/react-query';
import { apiCall } from '../config/api';

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  level: number;
  xp_points: number;
  total_trades: number;
  best_daily_return: number;
  trading_streak: number;
  rank: number;
}

export interface LeaderboardData {
  success: boolean;
  leaderboard: LeaderboardEntry[];
}

export const useLeaderboard = (limit: number = 50, enabled: boolean = true) => {
  const { data, isLoading, error, refetch } = useQuery<LeaderboardData, Error>({
    queryKey: ['leaderboard', limit],
    queryFn: async () => {
      try {
        const response = await apiCall(`/api/gamification/leaderboard?limit=${limit}`);
        return response;
      } catch (err) {
        console.warn('Leaderboard endpoint failed:', err);
        // Return empty leaderboard on error
        return {
          success: false,
          leaderboard: []
        };
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
    retry: 2,
    enabled
  });

  return {
    leaderboard: data?.leaderboard || [],
    isLoading,
    error,
    refetch
  };
};

