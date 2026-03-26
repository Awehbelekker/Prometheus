/**
 * LoadingOverlay Component
 * Full-screen loading overlay with progress indicator
 */

import React from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  LinearProgress
} from '@mui/material';

export interface LoadingOverlayProps {
  open: boolean;
  message?: string;
  progress?: number; // 0-100 for determinate progress
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  open,
  message = 'Loading...',
  progress
}) => {
  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999
      }}
    >
      <Box
        sx={{
          textAlign: 'center',
          p: 4,
          borderRadius: 2,
          background: 'rgba(26, 26, 26, 0.95)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          minWidth: 300
        }}
      >
        <CircularProgress
          size={60}
          sx={{ color: '#00d4ff', mb: 2 }}
          variant={progress !== undefined ? 'determinate' : 'indeterminate'}
          value={progress}
        />
        
        <Typography variant="h6" sx={{ color: '#fff', mb: 1 }}>
          {message}
        </Typography>
        
        {progress !== undefined && (
          <>
            <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
              {Math.round(progress)}% complete
            </Typography>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#00d4ff',
                  borderRadius: 3
                }
              }}
            />
          </>
        )}
      </Box>
    </Box>
  );
};

export default LoadingOverlay;

