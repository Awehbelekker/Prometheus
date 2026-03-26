/**
 * EmptyState Component
 * Reusable empty state component for various scenarios
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent
} from '@mui/material';
import {
  Inbox,
  TrendingUp,
  EmojiEvents,
  Assessment,
  AccountBalance,
  ShowChart,
  Notifications,
  People
} from '@mui/icons-material';

export interface EmptyStateProps {
  variant: 'portfolio' | 'trades' | 'achievements' | 'analytics' | 'positions' | 'notifications' | 'users' | 'custom';
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  variant,
  title,
  description,
  actionLabel,
  onAction,
  icon
}) => {
  const getDefaultContent = () => {
    switch (variant) {
      case 'portfolio':
        return {
          icon: <AccountBalance sx={{ fontSize: 80, color: '#00d4ff', opacity: 0.5 }} />,
          title: 'No Portfolio Data',
          description: 'Start trading to build your portfolio and track your investments.',
          actionLabel: 'Start Trading',
          color: '#00d4ff'
        };
      case 'trades':
        return {
          icon: <TrendingUp sx={{ fontSize: 80, color: '#4caf50', opacity: 0.5 }} />,
          title: 'No Trades Yet',
          description: 'You haven\'t made any trades yet. Start your trading journey now!',
          actionLabel: 'Make Your First Trade',
          color: '#4caf50'
        };
      case 'achievements':
        return {
          icon: <EmojiEvents sx={{ fontSize: 80, color: '#ff9800', opacity: 0.5 }} />,
          title: 'No Achievements Unlocked',
          description: 'Complete trades and challenges to unlock achievements and earn XP.',
          actionLabel: 'View Challenges',
          color: '#ff9800'
        };
      case 'analytics':
        return {
          icon: <Assessment sx={{ fontSize: 80, color: '#9c27b0', opacity: 0.5 }} />,
          title: 'No Analytics Data',
          description: 'Analytics will appear here once you start trading.',
          actionLabel: 'Start Trading',
          color: '#9c27b0'
        };
      case 'positions':
        return {
          icon: <ShowChart sx={{ fontSize: 80, color: '#2196f3', opacity: 0.5 }} />,
          title: 'No Open Positions',
          description: 'You don\'t have any open positions. Start trading to see your positions here.',
          actionLabel: 'Open Position',
          color: '#2196f3'
        };
      case 'notifications':
        return {
          icon: <Notifications sx={{ fontSize: 80, color: '#ff6b35', opacity: 0.5 }} />,
          title: 'No Notifications',
          description: 'You\'re all caught up! Notifications will appear here.',
          actionLabel: null,
          color: '#ff6b35'
        };
      case 'users':
        return {
          icon: <People sx={{ fontSize: 80, color: '#00d4ff', opacity: 0.5 }} />,
          title: 'No Users Found',
          description: 'No users match your search criteria.',
          actionLabel: 'Clear Filters',
          color: '#00d4ff'
        };
      case 'custom':
      default:
        return {
          icon: <Inbox sx={{ fontSize: 80, color: '#888', opacity: 0.5 }} />,
          title: 'No Data',
          description: 'There is no data to display.',
          actionLabel: null,
          color: '#888'
        };
    }
  };

  const defaultContent = getDefaultContent();
  const finalIcon = icon || defaultContent.icon;
  const finalTitle = title || defaultContent.title;
  const finalDescription = description || defaultContent.description;
  const finalActionLabel = actionLabel || defaultContent.actionLabel;

  return (
    <Card
      sx={{
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3,
        minHeight: 300
      }}
    >
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            py: 6,
            px: 3
          }}
        >
          {/* Icon */}
          <Box sx={{ mb: 3 }}>
            {finalIcon}
          </Box>

          {/* Title */}
          <Typography
            variant="h5"
            sx={{
              color: '#fff',
              fontWeight: 600,
              mb: 2
            }}
          >
            {finalTitle}
          </Typography>

          {/* Description */}
          <Typography
            variant="body1"
            sx={{
              color: '#aaa',
              mb: 4,
              maxWidth: 500
            }}
          >
            {finalDescription}
          </Typography>

          {/* Action Button */}
          {finalActionLabel && onAction && (
            <Button
              variant="contained"
              onClick={onAction}
              sx={{
                background: `linear-gradient(45deg, ${defaultContent.color}, ${defaultContent.color}dd)`,
                color: variant === 'achievements' || variant === 'notifications' ? '#000' : '#fff',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                '&:hover': {
                  background: `linear-gradient(45deg, ${defaultContent.color}dd, ${defaultContent.color}bb)`,
                  transform: 'scale(1.02)'
                }
              }}
            >
              {finalActionLabel}
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default EmptyState;

