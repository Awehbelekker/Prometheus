import React from 'react';
import { Box, Skeleton, Grid, Card, CardContent, Stack } from '@mui/material';

/**
 * Enhanced Skeleton for Admin Dashboard
 */
const AdminDashboardSkeleton: React.FC = () => {
  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
      p: 3
    }}>
      {/* Header Skeleton */}
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width={400} height={48} sx={{ mb: 2 }} />
        <Skeleton variant="text" width={300} height={24} />
      </Box>

      {/* Stats Cards Skeleton */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={i}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3
            }}>
              <CardContent sx={{ p: 2 }}>
                <Skeleton variant="text" width="70%" height={16} sx={{ mb: 1 }} />
                <Skeleton variant="text" width="100%" height={32} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Skeleton */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Skeleton variant="text" width={200} height={32} sx={{ mb: 3 }} />
              <Skeleton variant="rectangular" width="100%" height={400} borderRadius={2} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3
            }}>
              <CardContent sx={{ p: 3 }}>
                <Skeleton variant="text" width={150} height={24} sx={{ mb: 2 }} />
                {[1, 2, 3, 4].map((i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Skeleton variant="text" width="80%" height={20} />
                    <Skeleton variant="rectangular" width="100%" height={40} borderRadius={1} sx={{ mt: 1 }} />
                  </Box>
                ))}
              </CardContent>
            </Card>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3
            }}>
              <CardContent sx={{ p: 3 }}>
                <Skeleton variant="text" width={150} height={24} sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" width="100%" height={200} borderRadius={2} />
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboardSkeleton;

