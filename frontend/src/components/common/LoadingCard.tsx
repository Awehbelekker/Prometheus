import React from 'react';
import {
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Box,
  Skeleton,
  Stack
} from '@mui/material';

interface LoadingCardProps {
  message?: string;
  variant?: 'circular' | 'skeleton' | 'minimal';
  size?: 'small' | 'medium' | 'large';
  fullHeight?: boolean;
}

/**
 * Standardized Loading Card Component
 * 
 * Provides consistent loading states across all components
 */
const LoadingCard: React.FC<LoadingCardProps> = ({
  message = 'Loading data...',
  variant = 'circular',
  size = 'medium',
  fullHeight = false
}) => {
  const getProgressSize = () => {
    switch (size) {
      case 'small': return 32;
      case 'large': return 64;
      default: return 48;
    }
  };

  const getCardHeight = () => {
    if (fullHeight) return '100vh';
    switch (size) {
      case 'small': return 120;
      case 'large': return 300;
      default: return 200;
    }
  };

  const renderCircularLoading = () => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: getCardHeight(),
        textAlign: 'center'
      }}
    >
      <CircularProgress
        size={getProgressSize()}
        sx={{
          color: '#00d4ff',
          mb: 2,
          '& .MuiCircularProgress-circle': {
            strokeLinecap: 'round',
          }
        }}
      />
      <Typography
        variant={size === 'small' ? 'caption' : 'body2'}
        sx={{
          color: '#ccc',
          fontWeight: 500
        }}
      >
        {message}
      </Typography>
    </Box>
  );

  const renderSkeletonLoading = () => (
    <Box sx={{ p: size === 'small' ? 2 : 3 }}>
      <Stack spacing={2}>
        <Skeleton
          variant="text"
          width="60%"
          height={size === 'small' ? 20 : 28}
          sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }}
        />
        <Skeleton
          variant="rectangular"
          width="100%"
          height={size === 'small' ? 60 : size === 'large' ? 120 : 80}
          sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', borderRadius: 1 }}
        />
        <Stack direction="row" spacing={1}>
          <Skeleton
            variant="text"
            width="30%"
            height={size === 'small' ? 16 : 20}
            sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }}
          />
          <Skeleton
            variant="text"
            width="40%"
            height={size === 'small' ? 16 : 20}
            sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }}
          />
        </Stack>
      </Stack>
    </Box>
  );

  const renderMinimalLoading = () => (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: size === 'small' ? 60 : size === 'large' ? 120 : 80,
        gap: 2
      }}
    >
      <CircularProgress
        size={size === 'small' ? 20 : 24}
        sx={{ color: '#00d4ff' }}
      />
      <Typography
        variant="body2"
        sx={{ color: '#ccc' }}
      >
        {message}
      </Typography>
    </Box>
  );

  const renderContent = () => {
    switch (variant) {
      case 'skeleton':
        return renderSkeletonLoading();
      case 'minimal':
        return renderMinimalLoading();
      default:
        return renderCircularLoading();
    }
  };

  if (variant === 'minimal') {
    return (
      <Box
        sx={{
          backgroundColor: 'rgba(26, 26, 26, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          p: 2
        }}
      >
        {renderContent()}
      </Box>
    );
  }

  return (
    <Card
      sx={{
        background: 'rgba(26, 26, 26, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(0, 212, 255, 0.2)',
        borderRadius: 3,
        height: fullHeight ? '100vh' : 'auto'
      }}
    >
      <CardContent sx={{ p: variant === 'skeleton' ? 0 : 3 }}>
        {renderContent()}
      </CardContent>
    </Card>
  );
};

export default LoadingCard;
