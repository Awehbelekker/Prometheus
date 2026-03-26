import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Timeline,
  Assessment,
  Notifications,
  Settings
} from '@mui/icons-material';

interface PoolInvestorData {
  user_id: string;
  allocated_funds: number;
  current_value: number;
  total_return: number;
  total_return_percentage: number;
  daily_return: number;
  daily_return_percentage: number;
  compounding_effect: number;
  risk_metrics: {
    sharpe_ratio: number;
    max_drawdown: number;
    volatility: number;
  };
  recent_trades: Array<{
    symbol: string;
    side: string;
    quantity: number;
    price: number;
    timestamp: string;
    pnl: number;
  }>;
  performance_history: Array<{
    date: string;
    value: number;
    return_pct: number;
  }>;
}

const PoolInvestorDashboard: React.FC = () => {
  const [investorData, setInvestorData] = useState<PoolInvestorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInvestorData();
    const interval = setInterval(loadInvestorData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadInvestorData = async () => {
    try {
      const response = await fetch('/api/pool-investor/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setInvestorData(data);
      } else {
        setError('Failed to load investor data');
      }
    } catch (err) {
      setError('Network error loading data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading pool investor data...</Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  if (error || !investorData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error || 'No data available'}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
          💎 Pool Investor Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Notification Settings">
            <IconButton sx={{ color: '#00d4ff' }}>
              <Notifications />
            </IconButton>
          </Tooltip>
          <Tooltip title="Dashboard Settings">
            <IconButton sx={{ color: '#00d4ff' }}>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccountBalance sx={{ color: '#00d4ff', mr: 1 }} />
                <Typography variant="h6" sx={{ color: 'white' }}>Allocated Funds</Typography>
              </Box>
              <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                {formatCurrency(investorData.allocated_funds)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Timeline sx={{ color: '#4caf50', mr: 1 }} />
                <Typography variant="h6" sx={{ color: 'white' }}>Current Value</Typography>
              </Box>
              <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 600 }}>
                {formatCurrency(investorData.current_value)}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {formatPercentage(investorData.total_return_percentage)} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {investorData.daily_return >= 0 ? (
                  <TrendingUp sx={{ color: '#4caf50', mr: 1 }} />
                ) : (
                  <TrendingDown sx={{ color: '#f44336', mr: 1 }} />
                )}
                <Typography variant="h6" sx={{ color: 'white' }}>Daily Return</Typography>
              </Box>
              <Typography variant="h4" sx={{ 
                color: investorData.daily_return >= 0 ? '#4caf50' : '#f44336', 
                fontWeight: 600 
              }}>
                {formatCurrency(investorData.daily_return)}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {formatPercentage(investorData.daily_return_percentage)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(255, 107, 53, 0.2)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assessment sx={{ color: '#ff6b35', mr: 1 }} />
                <Typography variant="h6" sx={{ color: 'white' }}>Compounding Effect</Typography>
              </Box>
              <Typography variant="h4" sx={{ color: '#ff6b35', fontWeight: 600 }}>
                {formatCurrency(investorData.compounding_effect)}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Additional gains from compounding
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Risk Metrics */}
      <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'white', mb: 3 }}>
            📊 Risk Metrics (Your Allocated Portion Only)
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                  {investorData.risk_metrics.sharpe_ratio.toFixed(2)}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Sharpe Ratio
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#f44336', fontWeight: 600 }}>
                  {formatPercentage(investorData.risk_metrics.max_drawdown)}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Max Drawdown
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: '#ff9800', fontWeight: 600 }}>
                  {formatPercentage(investorData.risk_metrics.volatility)}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Volatility
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Recent Trades */}
      <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'white', mb: 3 }}>
            📈 Recent Trades (Your Allocated Portion)
          </Typography>
          <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#aaa' }}>Symbol</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Side</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Quantity</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Price</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>P&L</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Time</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {investorData.recent_trades.map((trade, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Typography sx={{ color: 'white', fontWeight: 600 }}>
                        {trade.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={trade.side.toUpperCase()}
                        sx={{
                          backgroundColor: trade.side === 'buy' ? '#4caf5020' : '#f4433620',
                          color: trade.side === 'buy' ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ color: 'white' }}>
                        {trade.quantity.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ color: 'white' }}>
                        {formatCurrency(trade.price)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography sx={{ 
                        color: trade.pnl >= 0 ? '#4caf50' : '#f44336',
                        fontWeight: 600
                      }}>
                        {formatCurrency(trade.pnl)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        {new Date(trade.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Performance History Chart Placeholder */}
      <Card sx={{ background: 'rgba(26, 26, 46, 0.95)', border: '1px solid rgba(0, 212, 255, 0.2)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ color: 'white', mb: 3 }}>
            📊 Performance History (Your Allocated Portion with Compounding)
          </Typography>
          <Box sx={{ 
            height: 300, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 2
          }}>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
              Performance chart will be implemented here
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PoolInvestorDashboard;
