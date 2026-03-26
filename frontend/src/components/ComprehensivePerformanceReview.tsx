import React, { useState, useEffect } from 'react';
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
  LinearProgress,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  People,
  AccountBalance,
  Timeline,
  Download,
  Refresh,
  FilterList,
  Star,
  Warning
} from '@mui/icons-material';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';


interface UserPerformance {
  userId: string;
  username: string;
  email: string;
  role: string;
  totalTrades: number;
  winRate: number;
  totalReturn: number;
  totalPnL: number;
  sharpeRatio: number;
  maxDrawdown: number;
  avgTradeSize: number;
  riskScore: number;
  lastActive: string;
  accountValue: number;
  tier: string;
}

interface TradeAnalysis {
  tradeId: string;
  userId: string;
  username: string;
  symbol: string;
  side: string;
  quantity: number;
  entryPrice: number;
  exitPrice: number;
  pnl: number;
  pnlPercent: number;
  duration: string;
  strategy: string;
  aiConfidence: number;
  timestamp: string;
  status: string;
}

interface PerformanceMetrics {
  totalUsers: number;
  activeUsers: number;
  totalTrades: number;
  totalVolume: number;
  avgWinRate: number;
  avgReturn: number;
  totalPnL: number;
  bestPerformer: string;
  worstPerformer: string;
  riskDistribution: { low: number; medium: number; high: number };
}

interface ComprehensivePerformanceReviewProps {
  user?: any;
}

const ComprehensivePerformanceReview: React.FC<ComprehensivePerformanceReviewProps> = ({ user }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('30d');
  const [sortBy, setSortBy] = useState('totalReturn');
  const [filterTier, setFilterTier] = useState('all');

  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    totalUsers: 0,
    activeUsers: 0,
    totalTrades: 0,
    totalVolume: 0,
    avgWinRate: 0,
    avgReturn: 0,
    totalPnL: 0,
    bestPerformer: '',
    worstPerformer: '',
    riskDistribution: { low: 0, medium: 0, high: 0 }
  });

  const [userPerformances, setUserPerformances] = useState<UserPerformance[]>([]);
  const [tradeAnalyses, setTradeAnalyses] = useState<TradeAnalysis[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [isRealTime, setIsRealTime] = useState(false);
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const [showDebug, setShowDebug] = useState(false);

  // Admin access check
  const isAdmin = user?.tier === 'admin' || user?.role === 'admin';

  useEffect(() => {
    if (isAdmin) {
      loadPerformanceData();

      // Set up real-time updates
      const interval = setInterval(() => {
        if (isRealTime) {
          loadPerformanceData();
        }
      }, 30000); // Update every 30 seconds when real-time is enabled

      return () => clearInterval(interval);
    }
  }, [timeframe, sortBy, filterTier, isAdmin, isRealTime]);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);

      const authHeader = { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` };
      const retryOpts = { retries: 4, backoffMs: 500, maxBackoffMs: 8000, timeoutMs: 10000 };

      // Load LIVE performance data from actual running system (with retry)
      const [metricsData, usersData, tradesData, demoData] = await Promise.all([
        getJsonWithRetry(getApiUrl(`/api/live-performance/system-metrics?timeframe=${timeframe}`), { headers: authHeader }, retryOpts),
        getJsonWithRetry(getApiUrl(`/api/live-performance/user-analytics?sort=${sortBy}&tier=${filterTier}&timeframe=${timeframe}`), { headers: authHeader }, retryOpts),
        getJsonWithRetry(getApiUrl(`/api/live-performance/trade-history?timeframe=${timeframe}&limit=100`), { headers: authHeader }, retryOpts),
        getJsonWithRetry(getApiUrl(`/api/live-performance/demo-analytics?timeframe=${timeframe}`), { headers: authHeader }, retryOpts)
      ]);

      setMetrics({
        ...metricsData.metrics,
        ...demoData.demo_metrics
      });
      setUserPerformances(usersData.users);
      setTradeAnalyses(tradesData.trades);
      setLastUpdated(new Date().toLocaleTimeString());

    } catch (err) {
      // API failed - show error and try to get basic data
      console.error('Performance data error:', err);
      setError('Failed to load performance data');
      setDebugInfo({ error: (err as any)?.message || String(err), timestamp: new Date().toISOString() });

      // Try to get basic system data as fallback
      try {
        const basicData = await getJsonWithRetry(getApiUrl('/api/system/status'), {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        }, { retries: 3, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
        setMetrics({
          totalUsers: basicData.users || 0,
          activeUsers: basicData.active_users || 0,
          totalTrades: basicData.trades || 0,
          totalVolume: basicData.volume || 0,
          avgWinRate: basicData.win_rate || 0,
          avgReturn: basicData.return_rate || 0,
          totalPnL: basicData.pnl || 0,
          bestPerformer: 'N/A',
          worstPerformer: 'N/A',
          riskDistribution: { low: 0, medium: 0, high: 0 }
        });
      } catch (fallbackError) {
        console.error('Fallback API also failed:', fallbackError);
      }

      // Populate with sample placeholders to maintain UI shape
      setUserPerformances([
        {
          userId: 'user_1',
          username: 'alex_trader',
          email: 'alex@example.com',
          role: 'premium',
          totalTrades: 342,
          winRate: 78.4,
          totalReturn: 45.7,
          totalPnL: 23847.92,
          sharpeRatio: 2.34,
          maxDrawdown: -8.2,
          avgTradeSize: 2500,
          riskScore: 6.2,
          lastActive: '2024-01-15T10:30:00Z',
          accountValue: 75847.92,
          tier: 'premium'
        },
        {
          userId: 'user_2',
          username: 'sarah_quant',
          email: 'sarah@example.com',
          role: 'premium',
          totalTrades: 198,
          winRate: 71.2,
          totalReturn: 32.1,
          totalPnL: 18293.45,
          sharpeRatio: 1.87,
          maxDrawdown: -12.4,
          avgTradeSize: 3200,
          riskScore: 7.1,
          lastActive: '2024-01-15T09:15:00Z',
          accountValue: 68293.45,
          tier: 'premium'
        }
      ]);

      setTradeAnalyses([
        {
          tradeId: 'trade_1',
          userId: 'user_1',
          username: 'alex_trader',
          symbol: 'AAPL',
          side: 'buy',
          quantity: 100,
          entryPrice: 150.25,
          exitPrice: 157.80,
          pnl: 755.00,
          pnlPercent: 5.02,
          duration: '2d 4h',
          strategy: 'momentum',
          aiConfidence: 0.87,
          timestamp: '2024-01-15T08:30:00Z',
          status: 'closed'
        }
      ]);

    } finally {
      setLoading(false);
    }
  };


  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'admin': return '#9c27b0';
      case 'premium': return '#ff6b35';
      case 'demo': return '#00d4ff';
      default: return '#4caf50';
    }
  };

  const getRiskColor = (score: number) => {
    if (score <= 3) return '#4caf50';
    if (score <= 7) return '#ff9800';
    return '#f44336';
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const exportData = () => {
    const data = {
      metrics,
      users: userPerformances,
      trades: tradeAnalyses,
      generatedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance_review_${timeframe}_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Access control - Admin only
  if (!isAdmin) {
    return (
      <Box sx={{
        p: 3,
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Card sx={{
          background: 'rgba(244, 67, 54, 0.1)',
          border: '1px solid #f44336',
          maxWidth: 500,
          textAlign: 'center'
        }}>
          <CardContent sx={{ p: 4 }}>
            <Warning sx={{ fontSize: 60, color: '#f44336', mb: 2 }} />
            <Typography variant="h5" sx={{ color: '#f44336', fontWeight: 700, mb: 2 }}>
              🔒 Admin Access Required
            </Typography>
            <Typography variant="body1" sx={{ color: '#aaa', mb: 3 }}>
              The Performance Review dashboard is restricted to administrators only.
              This feature provides comprehensive analytics across all users and trades.
            </Typography>
            <Typography variant="body2" sx={{ color: '#666' }}>
              Current Access Level: <Chip
                label={user?.tier || user?.role || 'Unknown'}
                sx={{
                  backgroundColor: '#ff6b35',
                  color: 'white',
                  fontWeight: 600,
                  ml: 1
                }}
              />
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, color: 'white' }}>
          Loading Performance Review...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
            📊 Comprehensive Performance Review
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
            <Chip
              label="🔒 ADMIN ONLY"
              sx={{
                backgroundColor: '#f44336',
                color: 'white',
                fontWeight: 700,
                fontSize: '0.75rem'
              }}
            />
            <Chip
              label={`📊 LIVE DATA ${isRealTime ? '🟢' : '⏸️'}`}
              onClick={() => setIsRealTime(!isRealTime)}
              sx={{
                backgroundColor: isRealTime ? '#4caf50' : '#ff9800',
                color: 'white',
                fontWeight: 600,
                fontSize: '0.75rem',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: isRealTime ? '#388e3c' : '#f57c00'
                }
              }}
            />
            <Typography variant="body2" sx={{ color: '#aaa' }}>
              Real-time analytics from live 48-hour trading system
            </Typography>
            {lastUpdated && (
              <Typography variant="caption" sx={{ color: '#666' }}>
                Last updated: {lastUpdated}
              </Typography>
            )}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel sx={{ color: '#aaa' }}>Timeframe</InputLabel>
            <Select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              sx={{ color: 'white' }}
            >
              <MenuItem value="7d">7 Days</MenuItem>
              <MenuItem value="30d">30 Days</MenuItem>
              <MenuItem value="90d">90 Days</MenuItem>
              <MenuItem value="1y">1 Year</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadPerformanceData}
            sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={exportData}
            sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
          >
            Export
          </Button>
          <Button
            variant="outlined"
            onClick={() => setShowDebug(!showDebug)}
            sx={{ color: '#ff9800', borderColor: '#ff9800' }}
          >
            Debug
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {showDebug && debugInfo && (
        <Card sx={{ mb: 3, background: 'rgba(255, 152, 0, 0.1)', border: '1px solid #ff9800' }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#ff9800', mb: 2 }}>
              🔧 Debug Information
            </Typography>
            <pre style={{ color: '#fff', fontSize: '0.8rem', overflow: 'auto' }}>
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
            <Typography variant="body2" sx={{ color: '#aaa', mt: 2 }}>
              Backend Server Status: {debugInfo.metrics === 200 ? '✅ Connected' : '❌ Disconnected'}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #00d4ff, #0099cc)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {metrics.totalUsers}
                  </Typography>
                  <Typography variant="body2">
                    Total Users ({metrics.activeUsers} active)
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff6b35, #e55a2b)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {metrics.totalTrades.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">
                    Total Trades
                  </Typography>
                </Box>
                <Timeline sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4caf50, #388e3c)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {formatCurrency(metrics.totalPnL)}
                  </Typography>
                  <Typography variant="body2">
                    Total P&L
                  </Typography>
                </Box>
                <AccountBalance sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #9c27b0, #7b1fa2)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {formatPercent(metrics.avgWinRate)}
                  </Typography>
                  <Typography variant="body2">
                    Average Win Rate
                  </Typography>
                </Box>
                <Assessment sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            '& .MuiTab-root': { color: '#aaa' },
            '& .Mui-selected': { color: '#00d4ff' }
          }}
        >
          <Tab label="User Performance" />
          <Tab label="Trade Analysis" />
          <Tab label="Risk Assessment" />
        </Tabs>

        <CardContent>
          {activeTab === 0 && (
            <Box>
              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel sx={{ color: '#aaa' }}>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    sx={{ color: 'white' }}
                  >
                    <MenuItem value="totalReturn">Total Return</MenuItem>
                    <MenuItem value="winRate">Win Rate</MenuItem>
                    <MenuItem value="sharpeRatio">Sharpe Ratio</MenuItem>
                    <MenuItem value="totalTrades">Total Trades</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel sx={{ color: '#aaa' }}>Tier</InputLabel>
                  <Select
                    value={filterTier}
                    onChange={(e) => setFilterTier(e.target.value)}
                    sx={{ color: 'white' }}
                  >
                    <MenuItem value="all">All Tiers</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                    <MenuItem value="premium">Premium</MenuItem>
                    <MenuItem value="demo">Demo</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <TableContainer component={Paper} sx={{ background: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>User</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Tier</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Trades</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Win Rate</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Total Return</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>P&L</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Sharpe</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Risk</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Account Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {userPerformances.map((user) => (
                      <TableRow key={user.userId}>
                        <TableCell sx={{ color: 'white' }}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {user.username}
                            </Typography>
                            <Typography variant="caption" sx={{ color: '#aaa' }}>
                              {user.email}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={user.tier.toUpperCase()}
                            sx={{
                              backgroundColor: getTierColor(user.tier),
                              color: 'white',
                              fontWeight: 600
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>{user.totalTrades}</TableCell>
                        <TableCell sx={{ color: 'white' }}>{formatPercent(user.winRate)}</TableCell>
                        <TableCell sx={{
                          color: user.totalReturn >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}>
                          {formatPercent(user.totalReturn)}
                        </TableCell>
                        <TableCell sx={{
                          color: user.totalPnL >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}>
                          {formatCurrency(user.totalPnL)}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>{user.sharpeRatio.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip
                            label={user.riskScore.toFixed(1)}
                            sx={{
                              backgroundColor: getRiskColor(user.riskScore),
                              color: 'white',
                              fontWeight: 600
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                          {formatCurrency(user.accountValue)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 3 }}>
                Recent Trade Analysis
              </Typography>
              <TableContainer component={Paper} sx={{ background: 'transparent' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Trade ID</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>User</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Symbol</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Side</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>P&L</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Return %</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Duration</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>Strategy</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 600 }}>AI Confidence</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {tradeAnalyses.map((trade) => (
                      <TableRow key={trade.tradeId}>
                        <TableCell sx={{ color: 'white', fontFamily: 'monospace' }}>
                          {trade.tradeId.slice(-8)}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>{trade.username}</TableCell>
                        <TableCell sx={{ color: 'white', fontWeight: 600 }}>{trade.symbol}</TableCell>
                        <TableCell>
                          <Chip
                            label={trade.side.toUpperCase()}
                            sx={{
                              backgroundColor: trade.side === 'buy' ? '#4caf50' : '#f44336',
                              color: 'white',
                              fontWeight: 600
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{
                          color: trade.pnl >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}>
                          {formatCurrency(trade.pnl)}
                        </TableCell>
                        <TableCell sx={{
                          color: trade.pnlPercent >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}>
                          {formatPercent(trade.pnlPercent)}
                        </TableCell>
                        <TableCell sx={{ color: 'white' }}>{trade.duration}</TableCell>
                        <TableCell sx={{ color: 'white' }}>{trade.strategy}</TableCell>
                        <TableCell sx={{ color: 'white' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={trade.aiConfidence * 100}
                              sx={{ width: 60, height: 6 }}
                            />
                            <Typography variant="caption">
                              {(trade.aiConfidence * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" sx={{ color: 'white', mb: 3 }}>
                Risk Assessment Overview
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(76, 175, 80, 0.1)', border: '1px solid #4caf50' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>
                        Low Risk Users
                      </Typography>
                      <Typography variant="h3" sx={{ color: '#4caf50', fontWeight: 700 }}>
                        {metrics.riskDistribution.low}%
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        Conservative trading approach
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(255, 152, 0, 0.1)', border: '1px solid #ff9800' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: '#ff9800', mb: 2 }}>
                        Medium Risk Users
                      </Typography>
                      <Typography variant="h3" sx={{ color: '#ff9800', fontWeight: 700 }}>
                        {metrics.riskDistribution.medium}%
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        Balanced risk-reward approach
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ background: 'rgba(244, 67, 54, 0.1)', border: '1px solid #f44336' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ color: '#f44336', mb: 2 }}>
                        High Risk Users
                      </Typography>
                      <Typography variant="h3" sx={{ color: '#f44336', fontWeight: 700 }}>
                        {metrics.riskDistribution.high}%
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        Aggressive trading strategies
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ComprehensivePerformanceReview;
