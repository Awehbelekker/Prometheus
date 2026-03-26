import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress,
  Avatar,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  AttachMoney,
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Security,
  Speed,
  Warning,
  CheckCircle,
  MonetizationOn
} from '@mui/icons-material';
import { apiCall } from '../../config/api';

interface User {
  id: string;
  name: string;
  email: string;
  investmentAmount: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
  status: 'paper_trading' | 'live_trading_active' | 'live_trading_pending';
  tier: 'silver' | 'gold' | 'platinum';
  joinDate: string;
  lastActivity: string;
}

interface PoolStats {
  totalCapital: number;
  totalAllocated: number;
  availableCash: number;
  totalPnL: number;
  totalPnLPercentage: number;
  activeUsers: number;
  liveUsers: number;
  paperUsers: number;
  alpacaAccountValue: number;
  alpacaBuyingPower: number;
}

const LiveTradingControlTab: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [poolStats, setPoolStats] = useState<PoolStats | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [activationDialog, setActivationDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const data = await apiCall('/api/admin/live-trading-stats');
      if (data.success) {
        setUsers(data.users);
        setPoolStats(data.poolStats);
      }
    } catch (err) {
      console.error('Failed to load live trading data:', err);
    }
  };

  const activateLiveTrading = async (user: User) => {
    setLoading(true);
    try {
      const result = await apiCall('/api/admin/activate-live-trading', {
        method: 'POST',
        body: JSON.stringify({
          userId: user.id,
          investmentAmount: user.investmentAmount
        })
      });
      if (result.success) {
        setSuccess(`Live trading activated for ${user.name} with $${user.investmentAmount.toLocaleString()}`);
        setActivationDialog(false);
        loadData();
      } else {
        setError(result.error || 'Failed to activate live trading');
      }
    } catch (err) {
      setError('Failed to activate live trading');
    } finally {
      setLoading(false);
    }
  };

  const deactivateLiveTrading = async (userId: string) => {
    setLoading(true);
    try {
      const result = await apiCall('/api/admin/deactivate-live-trading', {
        method: 'POST',
        body: JSON.stringify({ userId })
      });
      if (result.success) {
        setSuccess('Live trading deactivated');
        loadData();
      } else {
        setError(result.error || 'Failed to deactivate live trading');
      }
    } catch (err) {
      setError('Failed to deactivate live trading');
    } finally {
      setLoading(false);
    }
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live_trading_active': return 'success';
      case 'live_trading_pending': return 'warning';
      case 'paper_trading': return 'info';
      default: return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'platinum': return '#9c27b0';
      case 'gold': return '#ff9800';
      case 'silver': return '#9e9e9e';
      default: return '#2196f3';
    }
  };

  if (!poolStats) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
        💰 Live Trading Control Center
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Pool Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
            border: '2px solid #00d4ff'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalance sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                    {formatCurrency(poolStats.totalCapital)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Pool Capital
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
                <MonetizationOn sx={{ color: '#4caf50', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#4caf50' }}>
                    {formatCurrency(poolStats.alpacaAccountValue)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Alpaca Account Value
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
                {poolStats.totalPnL >= 0 ? (
                  <TrendingUp sx={{ color: '#4caf50', fontSize: 32 }} />
                ) : (
                  <TrendingDown sx={{ color: '#f44336', fontSize: 32 }} />
                )}
                <Box>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      fontWeight: 700, 
                      color: poolStats.totalPnL >= 0 ? '#4caf50' : '#f44336' 
                    }}
                  >
                    {formatCurrency(poolStats.totalPnL)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Pool P&L ({formatPercentage(poolStats.totalPnLPercentage)})
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
                <Speed sx={{ color: '#ff9800', fontSize: 32 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 700 }}>
                    {poolStats.liveUsers}/{poolStats.activeUsers}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Live Trading Users
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alpaca Integration Status */}
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
            🔗 Alpaca Live Trading Integration
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Account Value</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {formatCurrency(poolStats.alpacaAccountValue)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={85}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': { bgcolor: '#4caf50' }
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Buying Power</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {formatCurrency(poolStats.alpacaBuyingPower)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={65}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': { bgcolor: '#00d4ff' }
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* User Management Table */}
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            👥 User Live Trading Management
          </Typography>

          <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User</TableCell>
                  <TableCell>Investment</TableCell>
                  <TableCell>Current Value</TableCell>
                  <TableCell>P&L</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: getTierColor(user.tier) }}>
                          {user.name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {user.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {formatCurrency(user.investmentAmount)}
                      </Typography>
                      <Chip
                        label={user.tier.toUpperCase()}
                        size="small"
                        sx={{
                          bgcolor: getTierColor(user.tier),
                          color: 'white',
                          fontSize: '0.7rem'
                        }}
                      />
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {formatCurrency(user.currentValue)}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color: user.pnl >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatCurrency(user.pnl)}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: user.pnl >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatPercentage(user.pnlPercentage)}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Chip
                        label={user.status.replace('_', ' ').toUpperCase()}
                        color={getStatusColor(user.status)}
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </TableCell>
                    
                    <TableCell>
                      {user.status === 'paper_trading' && (
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<PlayArrow />}
                          onClick={() => {
                            setSelectedUser(user);
                            setActivationDialog(true);
                          }}
                          sx={{ 
                            background: 'linear-gradient(45deg, #4caf50, #45a049)',
                            mr: 1
                          }}
                        >
                          Activate Live
                        </Button>
                      )}
                      
                      {user.status === 'live_trading_active' && (
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<Stop />}
                          onClick={() => deactivateLiveTrading(user.id)}
                          color="error"
                        >
                          Deactivate
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Live Trading Activation Dialog */}
      <Dialog open={activationDialog} onClose={() => setActivationDialog(false)}>
        <DialogTitle>
          🚀 Activate Live Trading
        </DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Box sx={{ pt: 2 }}>
              <Alert severity="warning" sx={{ mb: 3 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  This will activate live trading with real money for {selectedUser.name}
                </Typography>
              </Alert>
              
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>User:</strong> {selectedUser.name}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>Investment Amount:</strong> {formatCurrency(selectedUser.investmentAmount)}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>Tier:</strong> {selectedUser.tier.toUpperCase()}
              </Typography>
              
              <Alert severity="info">
                This user's allocation will be added to the live trading pool and managed by the AI systems.
                They will see their proportional share of profits/losses in their dashboard.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActivationDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => selectedUser && activateLiveTrading(selectedUser)}
            variant="contained"
            color="success"
            disabled={loading}
            startIcon={<PlayArrow />}
          >
            {loading ? 'Activating...' : 'Activate Live Trading'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LiveTradingControlTab;
