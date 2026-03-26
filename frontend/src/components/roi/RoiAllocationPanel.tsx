import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, alpha } from '@mui/material';

interface AllocationWeights {
  admin_weight: number;
  user_weight: number;
  pool_total: number;
}

interface RoiAllocationPanelProps {
  adminAmount: number;
  userAmount: number;
  data?: AllocationWeights | null;
}

const RoiAllocationPanel: React.FC<RoiAllocationPanelProps> = ({ adminAmount, userAmount, data }) => {
  if (!data) return null;
  const adminPct = data.admin_weight * 100;
  const userPct = data.user_weight * 100;

  return (
    <Card sx={{
      mb: 3,
      backgroundColor: 'rgba(26,26,46,0.8)',
      border: '1px solid rgba(156, 39, 176, 0.3)'
    }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 1, color: '#9c27b0', fontWeight: 700 }}>
          Profit Allocation Pool
        </Typography>
        <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
          Admin Pool: ${adminAmount.toLocaleString()} · User Contribution: ${userAmount.toLocaleString()} · Total Pool: ${data.pool_total.toLocaleString()}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>ADMIN SHARE</Typography>
            <LinearProgress
              variant="determinate"
              value={adminPct}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: alpha('#9c27b0', 0.15),
                '& .MuiLinearProgress-bar': { backgroundColor: '#9c27b0' }
              }}
            />
            <Typography variant="caption" sx={{ color: '#9c27b0', fontWeight: 700 }}>
              {adminPct.toFixed(2)}%
            </Typography>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>USER SHARE</Typography>
            <LinearProgress
              variant="determinate"
              value={userPct}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: alpha('#4caf50', 0.15),
                '& .MuiLinearProgress-bar': { backgroundColor: '#4caf50' }
              }}
            />
            <Typography variant="caption" sx={{ color: '#4caf50', fontWeight: 700 }}>
              {userPct.toFixed(2)}%
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RoiAllocationPanel;
