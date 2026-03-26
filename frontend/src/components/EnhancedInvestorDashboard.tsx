import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Alert,
  Avatar,
  Divider,
  Stack,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  AccountBalance,
  ShowChart,
  Speed,
  Star,
  Refresh,
  Timeline,
  MonetizationOn,
  Security,
  Analytics
} from '@mui/icons-material';
import { useInvestorData } from '../hooks/useInvestorData';
import { useRealtimePortfolio } from '../hooks/useRealtimePortfolio';

interface EnhancedInvestorDashboardProps {
  userId: string;
}

const EnhancedInvestorDashboard: React.FC<EnhancedInvestorDashboardProps> = ({ userId }) => {
  // ✅ FIXED: Use real investor data from API
  const {
    profile: investorProfile,
    platformPerformance,
    recentActivity,
    isLoading: loading,
    error,
    lastUpdate
  } = useInvestorData(userId);

  // ✅ FIXED: Real-time updates via WebSocket
  const { isConnected } = useRealtimePortfolio(userId);

  // Handle loading state
  if (loading) {
    return (
      <Box sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)'
      }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ color: '#00d4ff', mb: 2 }} />
          <Typography variant="h6" sx={{ color: '#fff' }}>
            Loading investor dashboard...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Handle error state
  if (error || !investorProfile) {
    return (
      <Box sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)'
      }}>
        <Typography variant="h5" sx={{ color: '#f44336', mb: 2 }}>
          ⚠️ Failed to load investor data
        </Typography>
        <Typography variant="body1" sx={{ color: '#aaa', mb: 3 }}>
          {error?.toString() || 'No investor profile found'}
        </Typography>
        <Button
          variant="contained"
          onClick={() => window.location.reload()}
          sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  const handleRefresh = () => {
    window.location.reload();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'platinum': return '#9c27b0';
      case 'gold': return '#ff9800';
      case 'silver': return '#9e9e9e';
      default: return '#2196f3';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'profit': return <TrendingUp sx={{ color: '#4caf50' }} />;
      case 'loss': return <TrendingDown sx={{ color: '#f44336' }} />;
      case 'allocation': return <AttachMoney sx={{ color: '#00d4ff' }} />;
      case 'withdrawal': return <MonetizationOn sx={{ color: '#ff9800' }} />;
      default: return <ShowChart />;
    }
  };

  if (!investorProfile || !platformPerformance) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <LinearProgress sx={{ width: 300 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
      p: 3
    }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#fff' }}>
            💎 My Investment Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              label={`Last Update: ${lastUpdate}`}
              size="small"
              sx={{ color: 'text.secondary' }}
            />
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefresh}
              sx={{ borderColor: '#00d4ff', color: '#00d4ff' }}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {/* User Profile Card */}
        <Card sx={{ 
          background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
          border: `2px solid ${getTierColor(investorProfile.tier)}`
        }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Avatar 
                sx={{ 
                  width: 80, 
                  height: 80, 
                  bgcolor: getTierColor(investorProfile.tier),
                  fontSize: '2rem',
                  fontWeight: 700
                }}
              >
                {investorProfile.name.charAt(0)}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                  {investorProfile.name}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Chip
                    label={`${investorProfile.tier.toUpperCase()} TIER`}
                    sx={{
                      bgcolor: getTierColor(investorProfile.tier),
                      color: 'white',
                      fontWeight: 600
                    }}
                  />
                  <Chip
                    label={investorProfile.status.toUpperCase()}
                    color="success"
                    sx={{ fontWeight: 600 }}
                  />
                  <Chip
                    label={`Member since ${new Date(investorProfile.joinDate).toLocaleDateString()}`}
                    variant="outlined"
                  />
                </Box>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Risk Tolerance: {investorProfile.riskTolerance.toUpperCase()} • 
                  Investment Strategy: AI-Powered Revolutionary Trading
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Performance Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
            border: '1px solid #00d4ff'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalance sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                    {formatCurrency(investorProfile.currentValue)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Current Portfolio Value
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
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#4caf50' }}>
                    {formatCurrency(investorProfile.totalPnL)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Profit
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#4caf50' }}>
                    {formatPercentage(investorProfile.totalPnLPercentage)}
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
                <Timeline sx={{ color: '#ff9800', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#ff9800' }}>
                    {formatCurrency(investorProfile.dailyPnL)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Today's P&L
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#ff9800' }}>
                    {formatPercentage(investorProfile.dailyPnLPercentage)}
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
                <AttachMoney sx={{ color: '#9c27b0', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {formatCurrency(investorProfile.investmentAmount)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Initial Investment
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Platform Performance & Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                🚀 Platform Performance Overview
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                      {formatCurrency(platformPerformance.totalAUM)}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Total AUM
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 700, color: '#4caf50' }}>
                      {formatPercentage(platformPerformance.successRate)}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Success Rate
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 700 }}>
                      {platformPerformance.activeTraders}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Active Traders
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip
                      label={platformPerformance.tradingEngineStatus.toUpperCase()}
                      color="success"
                      sx={{ fontWeight: 600 }}
                    />
                    <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
                      Engine Status
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              <Alert 
                severity="info" 
                sx={{ mt: 3, bgcolor: 'rgba(0, 212, 255, 0.1)', border: '1px solid #00d4ff' }}
              >
                🤖 Revolutionary AI engines are actively trading your allocated funds across multiple strategies including options, crypto arbitrage, and market making.
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                📈 Recent Activity
              </Typography>
              
              <Stack spacing={2}>
                {recentActivity.map((activity) => (
                  <Box
                    key={activity.id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                      p: 2,
                      borderRadius: 2,
                      bgcolor: 'rgba(42, 42, 42, 0.5)'
                    }}
                  >
                    {getActivityIcon(activity.type)}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {formatCurrency(activity.amount)}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {activity.description}
                      </Typography>
                    </Box>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnhancedInvestorDashboard;
