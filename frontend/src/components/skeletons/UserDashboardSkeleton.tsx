import React from 'react';
import { Box, Skeleton, Grid, Card, CardContent, Stack, Avatar } from '@mui/material';

/**
 * Enhanced Skeleton for User Dashboard
 * Provides better perceived performance than loading spinners
 */
const UserDashboardSkeleton: React.FC = () => {
  return (
    <Box sx={{ 
      position: 'relative',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
      p: 3
    }}>
      {/* Header Skeleton */}
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width={400} height={48} sx={{ mb: 2 }} />
        <Skeleton variant="text" width={300} height={32} />
        
        {/* User Profile Card Skeleton */}
        <Card sx={{ 
          background: 'rgba(26, 26, 26, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 3,
          mb: 3,
          mt: 3
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Skeleton variant="circular" width={80} height={80} sx={{ mr: 3 }} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width={200} height={32} sx={{ mb: 1 }} />
                <Skeleton variant="text" width={250} height={24} sx={{ mb: 1.5 }} />
                <Skeleton variant="rectangular" width={120} height={28} borderRadius={1} />
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Skeleton variant="text" width={100} height={20} sx={{ mb: 0.5 }} />
                <Skeleton variant="text" width={120} height={28} />
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Portfolio Overview Skeleton */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3,
            height: '100%'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Skeleton variant="text" width={200} height={32} />
                <Skeleton variant="rectangular" width={60} height={24} borderRadius={1} />
              </Box>
              
              <Grid container spacing={3}>
                {[1, 2, 3, 4].map((i) => (
                  <Grid item xs={6} md={3} key={i}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Skeleton variant="text" width="80%" height={20} sx={{ mb: 1, mx: 'auto' }} />
                      <Skeleton variant="text" width="100%" height={36} />
                    </Box>
                  </Grid>
                ))}
              </Grid>

              <Box sx={{ mt: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Skeleton variant="text" width={150} height={20} />
                  <Skeleton variant="text" width={60} height={20} />
                </Box>
                <Skeleton variant="rectangular" width="100%" height={12} borderRadius={1} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(255, 107, 53, 0.3)',
            borderRadius: 3,
            height: '100%'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Skeleton variant="text" width={150} height={32} sx={{ mb: 3 }} />
              <Stack spacing={2}>
                <Skeleton variant="rectangular" width="100%" height={48} borderRadius={1} />
                <Skeleton variant="rectangular" width="100%" height={48} borderRadius={1} />
                <Skeleton variant="rectangular" width="100%" height={48} borderRadius={1} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Gamification Section Skeleton */}
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width={300} height={32} sx={{ mb: 1 }} />
        <Skeleton variant="text" width={400} height={20} sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={4} key={i}>
              <Card sx={{ 
                background: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3
              }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                    <Skeleton variant="circular" width={48} height={48} sx={{ mr: 2 }} />
                    <Skeleton variant="text" width={150} height={24} />
                  </Box>
                  <Skeleton variant="text" width="80%" height={20} sx={{ mb: 2.5 }} />
                  <Skeleton variant="text" width={100} height={48} sx={{ mb: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Skeleton variant="text" width={80} height={16} />
                    <Skeleton variant="text" width={60} height={16} />
                  </Box>
                  <Skeleton variant="rectangular" width="100%" height={10} borderRadius={1} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Social & Educational Features Skeleton */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2].map((i) => (
          <Grid item xs={12} md={6} key={i}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3
            }}>
              <CardContent sx={{ p: 3 }}>
                <Skeleton variant="text" width={200} height={32} sx={{ mb: 2 }} />
                {[1, 2, 3].map((j) => (
                  <Box key={j} sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                    <Box sx={{ flex: 1 }}>
                      <Skeleton variant="text" width="60%" height={20} sx={{ mb: 0.5 }} />
                      <Skeleton variant="text" width="40%" height={16} />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UserDashboardSkeleton;

