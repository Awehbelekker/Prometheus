/**
 * SkeletonLoader Component
 * Reusable skeleton loading states for different content types
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Skeleton,
  Grid
} from '@mui/material';

export interface SkeletonLoaderProps {
  variant: 'dashboard' | 'portfolio' | 'table' | 'chart' | 'card';
  count?: number;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant,
  count = 1
}) => {
  const renderDashboardSkeleton = () => (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Skeleton variant="text" width="40%" height={40} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
        <Skeleton variant="text" width="60%" height={24} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <CardContent>
                <Skeleton variant="text" width="60%" height={20} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                <Skeleton variant="text" width="80%" height={40} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <CardContent>
              <Skeleton variant="rectangular" width="100%" height={300} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', borderRadius: 2 }} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <CardContent>
              {[1, 2, 3].map((i) => (
                <Box key={i} sx={{ mb: 2 }}>
                  <Skeleton variant="text" width="70%" height={20} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                  <Skeleton variant="text" width="50%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderPortfolioSkeleton = () => (
    <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
      <CardContent sx={{ p: 3 }}>
        <Skeleton variant="text" width="40%" height={32} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mb: 3 }} />
        
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={6} md={3} key={i}>
              <Skeleton variant="text" width="60%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
              <Skeleton variant="text" width="80%" height={32} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mt: 1 }} />
            </Grid>
          ))}
        </Grid>
        
        <Skeleton variant="rectangular" width="100%" height={12} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mt: 3, borderRadius: 6 }} />
      </CardContent>
    </Card>
  );

  const renderTableSkeleton = () => (
    <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
      <CardContent sx={{ p: 3 }}>
        <Skeleton variant="text" width="30%" height={32} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />
        
        {Array.from({ length: count }).map((_, i) => (
          <Box key={i} sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Skeleton variant="circular" width={40} height={40} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width="60%" height={20} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
              <Skeleton variant="text" width="40%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
            </Box>
            <Skeleton variant="text" width="15%" height={20} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
          </Box>
        ))}
      </CardContent>
    </Card>
  );

  const renderChartSkeleton = () => (
    <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
      <CardContent sx={{ p: 3 }}>
        <Skeleton variant="text" width="40%" height={32} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />
        <Skeleton variant="rectangular" width="100%" height={300} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', borderRadius: 2 }} />
      </CardContent>
    </Card>
  );

  const renderCardSkeleton = () => (
    <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Skeleton variant="circular" width={48} height={48} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mr: 2 }} />
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="text" width="60%" height={24} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
            <Skeleton variant="text" width="40%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
          </Box>
        </Box>
        <Skeleton variant="text" width="100%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', mb: 1 }} />
        <Skeleton variant="text" width="80%" height={16} sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
      </CardContent>
    </Card>
  );

  switch (variant) {
    case 'dashboard':
      return renderDashboardSkeleton();
    case 'portfolio':
      return renderPortfolioSkeleton();
    case 'table':
      return renderTableSkeleton();
    case 'chart':
      return renderChartSkeleton();
    case 'card':
      return renderCardSkeleton();
    default:
      return null;
  }
};

export default SkeletonLoader;

