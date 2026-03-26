import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  AccountBalance,
  Security,
  VerifiedUser,
  MonetizationOn,
  Timeline
} from '@mui/icons-material';

import { apiCall } from '../config/api';

interface UserProfile {
  id: string;
  email: string;
  tier: 'demo' | 'starter' | 'professional' | 'enterprise';
  balance: number;
  verified: boolean;
  totalTrades: number;
  totalProfit: number;
  winRate: number;
  riskScore: number;
  joinDate: string;
}

interface PerformanceMetrics {
  totalReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  avgTradeReturn: number;
  totalTrades: number;
  profitFactor: number;
  riskScore: number;
  monthlyReturns: number[];
}

interface TierUpgradeProps {
  currentTier: string;
  onUpgrade: (newTier: string, amount: number) => void;
}

const TierUpgrade: React.FC<TierUpgradeProps> = ({ currentTier, onUpgrade }) => {
  const [selectedTier, setSelectedTier] = useState('');
  const [investmentAmount, setInvestmentAmount] = useState(1000);

  const tiers = {
    starter: {
      name: 'Starter',
      minInvestment: 1000,
      maxInvestment: 10000,
      features: ['Live Trading', 'Basic AI Strategies', 'Email Support'],
      fee: '2% performance fee'
    },
    professional: {
      name: 'Professional',
      minInvestment: 10000,
      maxInvestment: 100000,
      features: ['Advanced AI Strategies', 'Priority Support', 'Custom Risk Management'],
      fee: '1.5% performance fee'
    },
    enterprise: {
      name: 'Enterprise',
      minInvestment: 100000,
      maxInvestment: 1000000,
      features: ['Dedicated AI Agents', '24/7 Support', 'Custom Strategies', 'API Access'],
      fee: '1% performance fee'
    }
  };

  const handleUpgrade = () => {
    if (selectedTier && investmentAmount >= tiers[selectedTier as keyof typeof tiers].minInvestment) {
      onUpgrade(selectedTier, investmentAmount);
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <MonetizationOn sx={{ mr: 1, verticalAlign: 'middle' }} />
          Upgrade Your Trading Account
        </Typography>

        <Grid container spacing={3}>
          {Object.entries(tiers).map(([tier, details]) => (
            <Grid item xs={12} md={4} key={tier}>
              <Card
                variant={selectedTier === tier ? 'outlined' : 'elevation'}
                sx={{
                  cursor: 'pointer',
                  border: selectedTier === tier ? '2px solid #1976d2' : undefined,
                  '&:hover': { boxShadow: 3 }
                }}
                onClick={() => setSelectedTier(tier)}
              >
                <CardContent>
                  <Typography variant="h6" color="primary">
                    {details.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    ${details.minInvestment.toLocaleString()} - ${details.maxInvestment.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" display="block" gutterBottom>
                    {details.fee}
                  </Typography>

                  <Box sx={{ mt: 2 }}>
                    {details.features.map((feature, index) => (
                      <Chip
                        key={index}
                        label={feature}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {selectedTier && (
          <Box sx={{ mt: 3 }}>
            <TextField
              label="Investment Amount"
              type="number"
              value={investmentAmount}
              onChange={(e) => setInvestmentAmount(Number(e.target.value))}
              InputProps={{
                startAdornment: '$',
              }}
              helperText={`Minimum: $${tiers[selectedTier as keyof typeof tiers].minInvestment.toLocaleString()}`}
              sx={{ mr: 2 }}
            />
            <Button
              variant="contained"
              onClick={handleUpgrade}
              disabled={investmentAmount < tiers[selectedTier as keyof typeof tiers].minInvestment}
            >
              Upgrade to {tiers[selectedTier as keyof typeof tiers].name}
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const PerformanceDashboard: React.FC<{ userId: string }> = ({ userId }) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);

  useEffect(() => {
    fetchUserData();
    fetchPerformanceData();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      // Mock data for demo - replace with actual API call
      const mockUser: UserProfile = {
        id: userId,
        email: 'user@example.com',
        tier: 'demo',
        balance: 0,
        verified: false,
        totalTrades: 47,
        totalProfit: 2450.75,
        winRate: 0.64,
        riskScore: 35,
        joinDate: '2024-01-15'
      };
      setUserProfile(mockUser);
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPerformanceData = async () => {
    try {
      // Mock performance data - replace with actual API call
      const mockPerformance: PerformanceMetrics = {
        totalReturn: 24.5,
        sharpeRatio: 1.85,
        maxDrawdown: 8.2,
        winRate: 64,
        avgTradeReturn: 2.3,
        totalTrades: 47,
        profitFactor: 1.7,
        riskScore: 35,
        monthlyReturns: [2.1, 3.4, -1.2, 4.7, 1.8, 3.2, 2.9, -0.5, 3.1, 2.8, 1.9, 4.2]
      };
      setPerformance(mockPerformance);
    } catch (error) {
      console.error('Error fetching performance data:', error);
    }
  };

  const handleUpgrade = async (newTier: string, amount: number) => {
    try {
      // API call to upgrade user tier (preserve auth_token source)
      const token = localStorage.getItem('auth_token');
      const data = await apiCall('/api/trading/demo-upgrade', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: JSON.stringify({ userId, tier: newTier, amount })
      });

      setUserProfile(prev => prev ? { ...prev, tier: newTier as any, balance: amount } : null);
      setUpgradeDialogOpen(false);
    } catch (error) {
      console.error('Upgrade error:', error);
    }
  };

  if (loading || !userProfile || !performance) {
    return <LinearProgress />;
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'demo': return 'default';
      case 'starter': return 'primary';
      case 'professional': return 'secondary';
      case 'enterprise': return 'success';
      default: return 'default';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* User Profile Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h4" gutterBottom>
                Trading Performance Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {userProfile.email}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Chip
                  label={userProfile.tier.toUpperCase()}
                  color={getTierColor(userProfile.tier) as any}
                  sx={{ mr: 1 }}
                />
                {userProfile.verified ? (
                  <Chip
                    label="Verified"
                    color="success"
                    icon={<VerifiedUser />}
                  />
                ) : (
                  <Chip
                    label="Unverified"
                    color="warning"
                    icon={<Security />}
                  />
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'right' }}>
                {userProfile.tier === 'demo' ? (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => setUpgradeDialogOpen(true)}
                    startIcon={<MonetizationOn />}
                  >
                    Start Live Trading
                  </Button>
                ) : (
                  <Typography variant="h6">
                    Account Balance: {formatCurrency(userProfile.balance)}
                  </Typography>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Demo Performance Alert */}
      {userProfile.tier === 'demo' && (
        <Alert
          severity="info"
          sx={{ mb: 3 }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => setUpgradeDialogOpen(true)}
            >
              UPGRADE
            </Button>
          }
        >
          <strong>Demo Trading Results:</strong> These results show what you could have earned with real money.
          Ready to start live trading?
        </Alert>
      )}

      {/* Performance Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Total Return</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {formatPercentage(performance.totalReturn)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatCurrency(userProfile.totalProfit)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assessment sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Sharpe Ratio</Typography>
              </Box>
              <Typography variant="h4" color="primary.main">
                {performance.sharpeRatio.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Risk-adjusted return
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingDown sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Max Drawdown</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                -{formatPercentage(performance.maxDrawdown)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Largest loss period
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Timeline sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Win Rate</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {performance.winRate}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {performance.totalTrades} total trades
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upgrade Dialog */}
      <Dialog
        open={upgradeDialogOpen}
        onClose={() => setUpgradeDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Upgrade to Live Trading</DialogTitle>
        <DialogContent>
          <TierUpgrade
            currentTier={userProfile.tier}
            onUpgrade={handleUpgrade}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Recent Performance Chart would go here */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Monthly Performance
          </Typography>
          <Grid container spacing={1}>
            {performance.monthlyReturns.map((return_, index) => (
              <Grid item xs={1} key={index}>
                <Box
                  sx={{
                    height: 40,
                    bgcolor: return_ > 0 ? 'success.light' : 'error.light',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: 1
                  }}
                >
                  <Typography variant="caption">
                    {return_ > 0 ? '+' : ''}{return_.toFixed(1)}%
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PerformanceDashboard;
