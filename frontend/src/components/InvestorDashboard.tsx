import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Button,
  Alert,
  useTheme,
  alpha
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  People,
  ShowChart,
  Speed,
  AccountBalance,
  Star,
  Refresh,
  PlayArrow,
  Stop
} from '@mui/icons-material';
import { apiCall } from '../config/api';


interface InvestorDashboardProps {
  currentUser?: any;
}

interface PlatformPerformance {
  total_users: number;
  active_traders: number;
  live_trading_users: number;
  total_platform_pnl: number;
  total_trades_today: number;
  avg_user_return: number;
  top_performer_pnl: number;
  platform_success_rate: number;
  total_assets_under_management: number;
}

interface TopPerformer {
  user_id: string;
  total_pnl: number;
  win_rate: number;
  total_trades: number;
}

const InvestorDashboard: React.FC<InvestorDashboardProps> = ({ currentUser }) => {
  const theme = useTheme();
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [monitoringActive, setMonitoringActive] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  useEffect(() => {
    loadPerformanceData();
    const interval = setInterval(loadPerformanceData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      const data = await apiCall('/api/performance/real-time');
      setPerformanceData(data);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error loading performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startMonitoring = async () => {
    try {
      const data = await apiCall('/api/performance/start-monitoring', { method: 'POST' });
      if (data.success) {
        setMonitoringActive(true);
        await loadPerformanceData();
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
    }
  };

  const stopMonitoring = async () => {
    try {
      const data = await apiCall('/api/performance/stop-monitoring', { method: 'POST' });
      if (data.success) {
        setMonitoringActive(false);
      }
    } catch (error) {
      console.error('Error stopping monitoring:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const platformPerf: PlatformPerformance = performanceData?.platform_performance || {};
  const topPerformers: TopPerformer[] = performanceData?.top_performers || [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            💎 Investor Dashboard
          </Typography>
          <Typography variant="subtitle1" sx={{ color: 'text.secondary' }}>
            Real-time platform performance and user profits
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Last Update: {lastUpdate}
          </Typography>

          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadPerformanceData}
            disabled={loading}
          >
            Refresh
          </Button>

          {!monitoringActive ? (
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={startMonitoring}
              sx={{
                background: 'linear-gradient(45deg, #4caf50, #45a049)',
                '&:hover': { background: 'linear-gradient(45deg, #45a049, #3d8b40)' }
              }}
            >
              Start Monitoring
            </Button>
          ) : (
            <Button
              variant="contained"
              startIcon={<Stop />}
              onClick={stopMonitoring}
              sx={{
                background: 'linear-gradient(45deg, #f44336, #d32f2f)',
                '&:hover': { background: 'linear-gradient(45deg, #d32f2f, #b71c1c)' }
              }}
            >
              Stop Monitoring
            </Button>
          )}
        </Box>
      </Box>

      {/* Live Status Indicator */}
      <Alert
        severity={performanceData?.is_live ? 'success' : 'warning'}
        sx={{ mb: 3 }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          {performanceData?.is_live ? '🟢 LIVE TRADING ACTIVE' : '🟡 DEMO MODE'}
        </Typography>
        <Typography variant="body2">
          {performanceData?.is_live
            ? 'Real money trading with actual user profits and losses'
            : 'Demonstration mode - switch to live trading for real results'
          }
        </Typography>
      </Alert>

      {/* Key Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{
            background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
            border: '1px solid #00d4ff'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AttachMoney sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                    {formatCurrency(platformPerf.total_platform_pnl || 0)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Platform P&L
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
                <People sx={{ color: '#4caf50', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {platformPerf.live_trading_users || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Live Trading Users
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
                <ShowChart sx={{ color: '#ff9800', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {formatPercentage(platformPerf.platform_success_rate || 0)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Success Rate
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
                <AccountBalance sx={{ color: '#9c27b0', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {formatCurrency(platformPerf.total_assets_under_management || 0)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Assets Under Management
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Additional Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                📊 Trading Activity
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Total Users:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {platformPerf.total_users || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Active Traders:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {platformPerf.active_traders || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Trades Today:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {platformPerf.total_trades_today || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                💰 Profitability
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Avg User Return:</Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: (platformPerf.avg_user_return || 0) >= 0 ? '#4caf50' : '#f44336'
                  }}
                >
                  {formatCurrency(platformPerf.avg_user_return || 0)}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Top Performer:</Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#4caf50'
                  }}
                >
                  {formatCurrency(platformPerf.top_performer_pnl || 0)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(platformPerf.platform_success_rate || 0, 100)}
                sx={{
                  mt: 2,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: alpha('#ffffff', 0.1),
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: '#4caf50'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                ⚡ System Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: performanceData?.is_live ? '#4caf50' : '#ff9800'
                }} />
                <Typography variant="body2">
                  {performanceData?.is_live ? 'Live Trading' : 'Demo Mode'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: monitoringActive ? '#4caf50' : '#f44336'
                }} />
                <Typography variant="body2">
                  {monitoringActive ? 'Monitoring Active' : 'Monitoring Inactive'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Speed sx={{ color: '#00d4ff', fontSize: 16 }} />
                <Typography variant="body2">
                  Real-time Updates
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Top Performers Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            🏆 Top Performing Users (Real Money Results)
          </Typography>

          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Rank</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>User ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Total P&L</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Win Rate</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Total Trades</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {topPerformers.map((performer, index) => (
                  <TableRow key={performer.user_id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {index === 0 && <Star sx={{ color: '#ffd700', fontSize: 20 }} />}
                        #{index + 1}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {performer.user_id.substring(0, 8)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: performer.total_pnl >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatCurrency(performer.total_pnl)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatPercentage(performer.win_rate)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {performer.total_trades}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label="LIVE"
                        size="small"
                        sx={{
                          backgroundColor: '#4caf50',
                          color: '#ffffff',
                          fontWeight: 600
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}

                {topPerformers.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        No performance data available. Start live trading to see results.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress sx={{ borderRadius: 1 }} />
        </Box>
      )}
    </Box>
  );
};

export default InvestorDashboard;
