import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Avatar,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  AttachMoney,
  Analytics,
  Star,
  Speed,
  Security
} from '@mui/icons-material';

interface User {
  id: string;
  name: string;
  email: string;
  status: 'pending' | 'approved' | 'rejected' | 'active';
  investmentAmount: number;
  allocatedFunds: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
  joinDate: string;
  tier: 'silver' | 'gold' | 'platinum';
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
}

interface PlatformStats {
  totalUsers: number;
  activeUsers: number;
  pendingApprovals: number;
  totalAUM: number;
  totalPnL: number;
  dailyPnL: number;
  tradingEngineStatus: 'active' | 'inactive' | 'maintenance';
  successRate: number;
}

interface AnalyticsTabProps {
  users: User[];
  platformStats: PlatformStats;
  formatCurrency: (amount: number) => string;
  formatPercentage: (value: number) => string;
}

const AnalyticsTab: React.FC<AnalyticsTabProps> = ({
  users,
  platformStats,
  formatCurrency,
  formatPercentage
}) => {
  const activeUsers = users.filter(u => u.status === 'active');
  const topPerformers = activeUsers
    .sort((a, b) => b.pnlPercentage - a.pnlPercentage)
    .slice(0, 5);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'platinum': return '#9c27b0';
      case 'gold': return '#ff9800';
      case 'silver': return '#9e9e9e';
      default: return '#2196f3';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'aggressive': return '#f44336';
      case 'moderate': return '#ff9800';
      case 'conservative': return '#4caf50';
      default: return '#2196f3';
    }
  };

  const avgReturn = activeUsers.length > 0 
    ? activeUsers.reduce((sum, user) => sum + user.pnlPercentage, 0) / activeUsers.length 
    : 0;

  const totalInvested = users.reduce((sum, user) => sum + user.investmentAmount, 0);
  const totalCurrent = users.reduce((sum, user) => sum + user.currentValue, 0);
  const platformReturn = totalInvested > 0 ? ((totalCurrent - totalInvested) / totalInvested * 100) : 0;

  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
        📊 Platform Analytics & Performance
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Analytics sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                    {formatPercentage(platformReturn)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Platform Return
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUp sx={{ color: '#4caf50', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#4caf50' }}>
                    {formatPercentage(avgReturn)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Avg User Return
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <People sx={{ color: '#ff9800', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    {((activeUsers.length / platformStats.totalUsers) * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    User Retention
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Speed sx={{ color: '#9c27b0', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    {formatPercentage(platformStats.successRate)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Success Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Top Performers */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                🏆 Top Performers
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {topPerformers.map((user, index) => (
                  <Box
                    key={user.id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      borderRadius: 2,
                      bgcolor: 'rgba(42, 42, 42, 0.5)',
                      border: index === 0 ? '1px solid #ffd700' : 'none'
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          color: index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : 'text.primary',
                          minWidth: 24
                        }}
                      >
                        #{index + 1}
                      </Typography>
                      <Avatar sx={{ bgcolor: getTierColor(user.tier) }}>
                        {user.name.charAt(0)}
                      </Avatar>
                    </Box>
                    
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {user.name}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={user.tier.toUpperCase()}
                          size="small"
                          sx={{
                            bgcolor: getTierColor(user.tier),
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    </Box>
                    
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 700,
                          color: user.pnl >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatPercentage(user.pnlPercentage)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {formatCurrency(user.pnl)}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* User Distribution */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                👥 User Distribution
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* By Tier */}
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
                    By Investment Tier
                  </Typography>
                  {['platinum', 'gold', 'silver'].map((tier) => {
                    const tierUsers = users.filter(u => u.tier === tier);
                    const percentage = users.length > 0 ? (tierUsers.length / users.length * 100) : 0;
                    
                    return (
                      <Box key={tier} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {tier} ({tierUsers.length})
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {percentage.toFixed(1)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            bgcolor: 'rgba(255,255,255,0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: getTierColor(tier)
                            }
                          }}
                        />
                      </Box>
                    );
                  })}
                </Box>

                <Divider />

                {/* By Risk Tolerance */}
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary' }}>
                    By Risk Tolerance
                  </Typography>
                  {['aggressive', 'moderate', 'conservative'].map((risk) => {
                    const riskUsers = users.filter(u => u.riskTolerance === risk);
                    const percentage = users.length > 0 ? (riskUsers.length / users.length * 100) : 0;
                    
                    return (
                      <Box key={risk} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {risk} ({riskUsers.length})
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {percentage.toFixed(1)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            bgcolor: 'rgba(255,255,255,0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: getRiskColor(risk)
                            }
                          }}
                        />
                      </Box>
                    );
                  })}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsTab;
