import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Badge,
  LinearProgress
} from '@mui/material';
import {
  AttachMoney,
  TrendingUp,
  People,
  Security,
  Add,
  Visibility,
  PlayArrow,
  History,
  AdminPanelSettings,
  AccountBalance,
  Assessment
} from '@mui/icons-material';
import { apiCall } from '../config/api';

interface UserSummary {
  user_id: string;
  tier: string;
  paper_trading_enabled: boolean;
  live_trading_enabled: boolean;
  allocated_funds: number;
  total_trades: number;
  total_profit_loss: number;
  achievements_count: number;
  current_level: number;
}

interface AdminDashboard {
  total_users: number;
  paper_only_users: number;
  live_approved_users: number;
  total_allocated_funds: number;
  active_sessions: number;
  recent_allocations: any[];
}

const AdminFundAllocationDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AdminDashboard | null>(null);
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<UserSummary | null>(null);
  const [allocationDialog, setAllocationDialog] = useState(false);
  const [activationDialog, setActivationDialog] = useState(false);
  const [allocationAmount, setAllocationAmount] = useState('');
  const [allocationReason, setAllocationReason] = useState('');
  const [activationReason, setActivationReason] = useState('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    loadDashboardData();
    loadUsers();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await apiCall('/api/admin/dashboard', {
        headers: { 'X-Admin-ID': 'admin_prometheus_001' }
      });
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await apiCall('/api/admin/users', {
        headers: { 'X-Admin-ID': 'admin_prometheus_001' }
      });
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAllocateFunds = async () => {
    if (!selectedUser || !allocationAmount) return;

    try {
      await apiCall('/api/admin/allocate-funds', {
        method: 'POST',
        headers: { 'X-Admin-ID': 'admin_prometheus_001' },
        body: JSON.stringify({
          user_id: selectedUser.user_id,
          amount: parseFloat(allocationAmount),
          reason: allocationReason
        })
      });

      setAlert({ type: 'success', message: `$${allocationAmount} allocated successfully!` });
      setAllocationDialog(false);
      setAllocationAmount('');
      setAllocationReason('');
      loadUsers();
      loadDashboardData();
    } catch (error: any) {
      setAlert({ type: 'error', message: error?.message || 'Failed to allocate funds' });
    }
  };

  const handleActivateLiveTrading = async () => {
    if (!selectedUser) return;

    try {
      await apiCall('/api/admin/activate-live-trading', {
        method: 'POST',
        headers: { 'X-Admin-ID': 'admin_prometheus_001' },
        body: JSON.stringify({
          user_id: selectedUser.user_id,
          reason: activationReason
        })
      });

      setAlert({ type: 'success', message: 'Live trading activated successfully!' });
      setActivationDialog(false);
      setActivationReason('');
      loadUsers();
      loadDashboardData();
    } catch (error: any) {
      setAlert({ type: 'error', message: error?.message || 'Failed to activate live trading' });
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'paper_only': return 'default';
      case 'live_approved': return 'success';
      case 'admin': return 'error';
      default: return 'default';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'paper_only': return '📄';
      case 'live_approved': return '💰';
      case 'admin': return '👑';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AdminPanelSettings sx={{ color: 'primary.main' }} />
          Admin Fund Allocation Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage user permissions, fund allocations, and live trading activation
        </Typography>
      </Box>

      {/* Alert */}
      {alert && (
        <Alert 
          severity={alert.type} 
          onClose={() => setAlert(null)}
          sx={{ mb: 3 }}
        >
          {alert.message}
        </Alert>
      )}

      {/* Dashboard Stats */}
      {dashboardData && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Users
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {dashboardData.total_users}
                    </Typography>
                  </Box>
                  <People sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Paper Only
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {dashboardData.paper_only_users}
                    </Typography>
                  </Box>
                  <Security sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Live Approved
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      {dashboardData.live_approved_users}
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Allocated
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700 }}>
                      ${dashboardData.total_allocated_funds.toLocaleString()}
                    </Typography>
                  </Box>
                  <AttachMoney sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Users Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccountBalance />
            User Management
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User ID</TableCell>
                  <TableCell>Tier</TableCell>
                  <TableCell>Allocated Funds</TableCell>
                  <TableCell>Total Trades</TableCell>
                  <TableCell>P&L</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Achievements</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.user_id}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {user.user_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${getTierIcon(user.tier)} ${user.tier.replace('_', ' ').toUpperCase()}`}
                        color={getTierColor(user.tier) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: user.allocated_funds > 0 ? 700 : 400 }}>
                        ${user.allocated_funds.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>{user.total_trades}</TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: user.total_profit_loss >= 0 ? 'success.main' : 'error.main',
                          fontWeight: 600
                        }}
                      >
                        ${user.total_profit_loss.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Badge badgeContent={user.current_level} color="primary">
                        <Assessment />
                      </Badge>
                    </TableCell>
                    <TableCell>{user.achievements_count}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Allocate Funds">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedUser(user);
                              setAllocationDialog(true);
                            }}
                          >
                            <Add />
                          </IconButton>
                        </Tooltip>
                        
                        {user.allocated_funds > 0 && !user.live_trading_enabled && (
                          <Tooltip title="Activate Live Trading">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => {
                                setSelectedUser(user);
                                setActivationDialog(true);
                              }}
                            >
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Fund Allocation Dialog */}
      <Dialog open={allocationDialog} onClose={() => setAllocationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Allocate Funds to {selectedUser?.user_id}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Amount ($)"
            type="number"
            fullWidth
            variant="outlined"
            value={allocationAmount}
            onChange={(e) => setAllocationAmount(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Reason (optional)"
            multiline
            rows={3}
            fullWidth
            variant="outlined"
            value={allocationReason}
            onChange={(e) => setAllocationReason(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAllocationDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAllocateFunds} 
            variant="contained"
            disabled={!allocationAmount || parseFloat(allocationAmount) <= 0}
          >
            Allocate Funds
          </Button>
        </DialogActions>
      </Dialog>

      {/* Live Trading Activation Dialog */}
      <Dialog open={activationDialog} onClose={() => setActivationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Activate Live Trading for {selectedUser?.user_id}</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will enable live trading with real money for this user. Make sure they have sufficient allocated funds.
          </Alert>
          <TextField
            margin="dense"
            label="Activation Reason"
            multiline
            rows={3}
            fullWidth
            variant="outlined"
            value={activationReason}
            onChange={(e) => setActivationReason(e.target.value)}
            placeholder="Reason for activating live trading..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActivationDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleActivateLiveTrading} 
            variant="contained"
            color="warning"
          >
            Activate Live Trading
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminFundAllocationDashboard;
