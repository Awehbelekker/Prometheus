import React from 'react';
import { Box, Skeleton, Grid, Card, CardContent, Stack } from '@mui/material';

/**
 * Enhanced Skeleton for Trading Dashboard
 */
const TradingDashboardSkeleton: React.FC = () => {
  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
      p: 3
    }}>
      {/* Header Skeleton */}
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width={300} height={48} sx={{ mb: 2 }} />
        <Skeleton variant="text" width={200} height={24} />
      </Box>

      {/* Stats Cards Skeleton */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3
            }}>
              <CardContent sx={{ p: 3 }}>
                <Skeleton variant="text" width="60%" height={20} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="100%" height={36} sx={{ mb: 1 }} />
                <Skeleton variant="rectangular" width="80%" height={40} borderRadius={1} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Portfolio & Chart Skeleton */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Skeleton variant="text" width={200} height={32} sx={{ mb: 3 }} />
              <Skeleton variant="rectangular" width="100%" height={300} borderRadius={2} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(255, 107, 53, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Skeleton variant="text" width={150} height={32} sx={{ mb: 3 }} />
              <Stack spacing={2}>
                {[1, 2, 3, 4].map((i) => (
                  <Box key={i}>
                    <Skeleton variant="text" width="70%" height={20} sx={{ mb: 0.5 }} />
                    <Skeleton variant="rectangular" width="100%" height={60} borderRadius={1} />
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Trading Signals Skeleton */}
      <Card sx={{ 
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3
      }}>
        <CardContent sx={{ p: 3 }}>
          <Skeleton variant="text" width={200} height={32} sx={{ mb: 3 }} />
          <Grid container spacing={2}>
            {[1, 2, 3].map((i) => (
              <Grid item xs={12} md={4} key={i}>
                <Skeleton variant="rectangular" width="100%" height={120} borderRadius={2} />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TradingDashboardSkeleton;

