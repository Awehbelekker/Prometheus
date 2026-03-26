/**
 * useGamification Hook
 * Fetches real gamification data from backend
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiCall } from '../config/api';
import { useSnackbar } from 'notistack';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  rarity?: string;
  earned_at?: string;
}

export interface Badge {
  type: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  rarity: string;
  earned_at: string;
}

export interface SkillRatings {
  risk_management: number;
  market_analysis: number;
  timing: number;
  portfolio_management: number;
  consistency: number;
}

export interface GamificationProgress {
  level: number;
  xp: number;
  achievements: Achievement[];
  skillRatings: SkillRatings;
  badges: Badge[];
  streak: number;
  nextLevelXP?: number;
  xpToNextLevel?: number;
  totalAchievements?: number;
}

export const useGamification = (userId: string, enabled: boolean = true) => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const { data, isLoading, error } = useQuery({
    queryKey: ['gamification', userId],
    queryFn: async () => {
      try {
        // Backend endpoint uses authenticated user from token, not userId in path
        const response = await apiCall(`/api/gamification/progress`);
        
        return {
          level: response.level || 1,
          xp: response.xp_points || 0,
          achievements: response.recent_achievements || [],
          skillRatings: response.skill_ratings || {
            risk_management: 0,
            market_analysis: 0,
            timing: 0,
            portfolio_management: 0,
            consistency: 0
          },
          badges: response.badges_earned || [],
          streak: response.current_streak || 0,
          nextLevelXP: response.next_level_xp || 1000,
          xpToNextLevel: response.xp_to_next_level || 1000,
          totalAchievements: response.total_achievements || 0
        } as GamificationProgress;
      } catch (err) {
        console.warn('Gamification endpoint failed, using defaults:', err);
        
        // Return default values if API fails
        return {
          level: 1,
          xp: 0,
          achievements: [],
          skillRatings: {
            risk_management: 0,
            market_analysis: 0,
            timing: 0,
            portfolio_management: 0,
            consistency: 0
          },
          badges: [],
          streak: 0,
          nextLevelXP: 1000,
          xpToNextLevel: 1000,
          totalAchievements: 0
        } as GamificationProgress;
      }
    },
    staleTime: 60000, // 1 minute
    refetchInterval: 120000, // Refetch every 2 minutes
    retry: 3,
    enabled
  });

  // Award XP mutation
  const awardXP = useMutation({
    mutationFn: async ({ amount, reason }: { amount: number; reason: string }) => {
      return await apiCall('/api/gamification/award-xp', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          xp_amount: amount,
          reason
        })
      });
    },
    onSuccess: (response) => {
      // Update cache optimistically
      queryClient.setQueryData(['gamification', userId], (old: any) => ({
        ...old,
        xp: response.new_xp || old.xp + response.xp_amount,
        level: response.new_level || old.level
      }));

      // Show notification
      if (response.level_up) {
        enqueueSnackbar(
          `🎉 Level Up! You're now level ${response.new_level}!`,
          { variant: 'success', autoHideDuration: 5000 }
        );
      } else {
        enqueueSnackbar(
          `+${response.xp_amount || 0} XP earned!`,
          { variant: 'info', autoHideDuration: 2000 }
        );
      }
    },
    onError: (error) => {
      console.error('Failed to award XP:', error);
      enqueueSnackbar('Failed to award XP', { variant: 'error' });
    }
  });

  // Unlock achievement mutation
  const unlockAchievement = useMutation({
    mutationFn: async (achievementId: string) => {
      return await apiCall('/api/gamification/unlock-achievement', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          achievement_id: achievementId
        })
      });
    },
    onSuccess: (response) => {
      // Invalidate cache to refetch
      queryClient.invalidateQueries({ queryKey: ['gamification', userId] });

      // Show achievement notification
      enqueueSnackbar(
        `🏆 Achievement Unlocked: ${response.achievement?.name || 'New Achievement'}!`,
        { variant: 'success', autoHideDuration: 5000 }
      );
    },
    onError: (error) => {
      console.error('Failed to unlock achievement:', error);
    }
  });

  return {
    level: data?.level || 1,
    xp: data?.xp || 0,
    achievements: data?.achievements || [],
    skillRatings: data?.skillRatings || {
      risk_management: 0,
      market_analysis: 0,
      timing: 0,
      portfolio_management: 0,
      consistency: 0
    },
    badges: data?.badges || [],
    streak: data?.streak || 0,
    nextLevelXP: data?.nextLevelXP || 1000,
    xpToNextLevel: data?.xpToNextLevel || 1000,
    totalAchievements: data?.totalAchievements || 0,
    isLoading,
    error,
    awardXP: awardXP.mutate,
    unlockAchievement: unlockAchievement.mutate
  };
};

