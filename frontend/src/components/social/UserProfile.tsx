/**
 * UserProfile Component
 * Display user profile with social features (follow, stats, achievements)
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  Chip,
  Grid,
  Divider,
  LinearProgress,
  IconButton
} from '@mui/material';
import {
  PersonAdd,
  PersonRemove,
  Share,
  EmojiEvents,
  TrendingUp,
  Star,
  LocalFireDepartment
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { apiCall } from '../../config/api';

interface UserProfileProps {
  userId: string;
  currentUserId?: string;
}

interface UserProfileData {
  userId: string;
  username: string;
  avatar?: string;
  bio?: string;
  level: number;
  xp: number;
  nextLevelXP: number;
  totalReturn: number;
  returnPercentage: number;
  winRate: number;
  totalTrades: number;
  streak: number;
  followers: number;
  following: number;
  isFollowing: boolean;
  badges: Array<{
    icon: string;
    name: string;
    rarity: string;
  }>;
  recentAchievements: Array<{
    name: string;
    icon: string;
    earnedAt: string;
  }>;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, currentUserId }) => {
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ['user-profile', userId],
    queryFn: async () => {
      const response = await apiCall(`/api/users/${userId}/profile`);
      return response as UserProfileData;
    }
  });

  const followMutation = useMutation({
    mutationFn: async () => {
      return await apiCall(`/api/users/${userId}/follow`, {
        method: 'POST'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile', userId] });
      enqueueSnackbar('Successfully followed user!', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('Failed to follow user', { variant: 'error' });
    }
  });

  const unfollowMutation = useMutation({
    mutationFn: async () => {
      return await apiCall(`/api/users/${userId}/unfollow`, {
        method: 'POST'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile', userId] });
      enqueueSnackbar('Successfully unfollowed user', { variant: 'info' });
    },
    onError: () => {
      enqueueSnackbar('Failed to unfollow user', { variant: 'error' });
    }
  });

  const handleFollowToggle = () => {
    if (profile?.isFollowing) {
      unfollowMutation.mutate();
    } else {
      followMutation.mutate();
    }
  };

  const handleShare = () => {
    const url = `${window.location.origin}/profile/${userId}`;
    navigator.clipboard.writeText(url);
    enqueueSnackbar('Profile link copied to clipboard!', { variant: 'success' });
  };

  if (isLoading || !profile) {
    return (
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <CardContent sx={{ p: 3 }}>
          <LinearProgress />
        </CardContent>
      </Card>
    );
  }

  const isOwnProfile = currentUserId === userId;

  return (
    <Card
      sx={{
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 3
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
          <Avatar
            src={profile.avatar}
            sx={{
              width: 80,
              height: 80,
              border: '3px solid #00d4ff',
              mr: 3
            }}
          >
            {profile.username[0].toUpperCase()}
          </Avatar>

          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700 }}>
                {profile.username}
              </Typography>
              <Chip
                label={`Level ${profile.level}`}
                size="small"
                sx={{
                  bgcolor: 'rgba(0, 212, 255, 0.2)',
                  color: '#00d4ff',
                  fontWeight: 600
                }}
              />
            </Box>

            {profile.bio && (
              <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                {profile.bio}
              </Typography>
            )}

            {/* Stats */}
            <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
              <Box>
                <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                  {profile.followers}
                </Typography>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  Followers
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                  {profile.following}
                </Typography>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  Following
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                  {profile.totalTrades}
                </Typography>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  Trades
                </Typography>
              </Box>
            </Box>

            {/* Actions */}
            {!isOwnProfile && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant={profile.isFollowing ? 'outlined' : 'contained'}
                  startIcon={profile.isFollowing ? <PersonRemove /> : <PersonAdd />}
                  onClick={handleFollowToggle}
                  disabled={followMutation.isPending || unfollowMutation.isPending}
                  sx={{
                    background: profile.isFollowing ? 'transparent' : 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    color: profile.isFollowing ? '#00d4ff' : '#000',
                    borderColor: '#00d4ff'
                  }}
                >
                  {profile.isFollowing ? 'Unfollow' : 'Follow'}
                </Button>
                <IconButton onClick={handleShare} sx={{ color: '#888' }}>
                  <Share />
                </IconButton>
              </Box>
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

        {/* XP Progress */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" sx={{ color: '#aaa' }}>
              XP Progress
            </Typography>
            <Typography variant="body2" sx={{ color: '#00d4ff' }}>
              {profile.xp.toLocaleString()} / {profile.nextLevelXP.toLocaleString()}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={(profile.xp / profile.nextLevelXP) * 100}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: 'rgba(255, 255, 255, 0.1)',
              '& .MuiLinearProgress-bar': {
                bgcolor: '#00d4ff',
                borderRadius: 4
              }
            }}
          />
        </Box>

        {/* Performance Stats */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
              <TrendingUp sx={{ color: '#4caf50', fontSize: 32, mb: 1 }} />
              <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 700 }}>
                +{profile.returnPercentage.toFixed(1)}%
              </Typography>
              <Typography variant="caption" sx={{ color: '#888' }}>
                Total Return
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(0, 212, 255, 0.1)', borderRadius: 2 }}>
              <EmojiEvents sx={{ color: '#00d4ff', fontSize: 32, mb: 1 }} />
              <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700 }}>
                {profile.winRate.toFixed(1)}%
              </Typography>
              <Typography variant="caption" sx={{ color: '#888' }}>
                Win Rate
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 2 }}>
              <LocalFireDepartment sx={{ color: '#ff9800', fontSize: 32, mb: 1 }} />
              <Typography variant="h6" sx={{ color: '#ff9800', fontWeight: 700 }}>
                {profile.streak}
              </Typography>
              <Typography variant="caption" sx={{ color: '#888' }}>
                Day Streak
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'rgba(255, 215, 0, 0.1)', borderRadius: 2 }}>
              <Star sx={{ color: '#ffd700', fontSize: 32, mb: 1 }} />
              <Typography variant="h6" sx={{ color: '#ffd700', fontWeight: 700 }}>
                {profile.badges.length}
              </Typography>
              <Typography variant="caption" sx={{ color: '#888' }}>
                Badges
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Recent Achievements */}
        {profile.recentAchievements.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ color: '#fff', mb: 2, fontWeight: 600 }}>
              Recent Achievements
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {profile.recentAchievements.map((achievement, index) => (
                <Chip
                  key={index}
                  label={achievement.name}
                  icon={<span style={{ fontSize: 20 }}>{achievement.icon}</span>}
                  sx={{
                    bgcolor: 'rgba(255, 152, 0, 0.2)',
                    color: '#ff9800',
                    fontWeight: 600
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default UserProfile;

