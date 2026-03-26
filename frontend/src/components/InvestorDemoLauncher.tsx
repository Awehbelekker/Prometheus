import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  AttachMoney,
  Speed,
  Psychology,
  Timeline,
  PlayArrow,
  Stop,
  Refresh,
  Close,
  ShowChart,
  TrendingDown
} from '@mui/icons-material';
import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';

interface InvestorDemoLauncherProps {
  currentUser?: any;
}

interface DemoTier {
  amount: number;
  name: string;
  risk_level: string;
  target_return: number;
  max_drawdown: number;
  trades_per_hour: number;
  description: string;
}

const InvestorDemoLauncher: React.FC<InvestorDemoLauncherProps> = ({ currentUser }) => {
  const theme = useTheme();
  const [demoForm, setDemoForm] = useState({
    investor_name: '',
    investor_email: '',
    investment_amount: 1000
  });
  const [activeDemos, setActiveDemos] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [engineRunning, setEngineRunning] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState<any>(null);

  const demoTiers: DemoTier[] = [
    {
      amount: 500,
      name: "Starter Demo",
      risk_level: "Conservative",
      target_return: 8,
      max_drawdown: 3,
      trades_per_hour: 2,
      description: "Perfect for first-time investors to see our AI in action"
    },
    {
      amount: 1000,
      name: "Standard Demo",
      risk_level: "Moderate",
      target_return: 12,
      max_drawdown: 5,
      trades_per_hour: 3,
      description: "Balanced approach showing consistent profit generation"
    },
    {
      amount: 2500,
      name: "Premium Demo",
      risk_level: "Moderate",
      target_return: 15,
      max_drawdown: 6,
      trades_per_hour: 4,
      description: "Enhanced returns with advanced AI strategies"
    },
    {
      amount: 5000,
      name: "Elite Demo",
      risk_level: "Aggressive",
      target_return: 20,
      max_drawdown: 8,
      trades_per_hour: 5,
      description: "Maximum profit potential with cutting-edge AI"
    }
  ];

  useEffect(() => {
    loadActiveDemos();
    const interval = setInterval(loadActiveDemos, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadActiveDemos = async () => {
    try {
      const data = await getJsonWithRetry<any[]>(getApiUrl('/api/demo/active'), {}, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 6000 });
      setActiveDemos(data || []);
    } catch (error) {
      console.error('Error loading active demos:', error);
    }
  };

  const startDemoEngine = async () => {
    try {
      setLoading(true);
      const data = await getJsonWithRetry<any>(getApiUrl('/api/demo/start-engine'), { method: 'POST' }, { retries: 2, backoffMs: 300, maxBackoffMs: 2000, timeoutMs: 5000 });
      if (data?.success) {
        setEngineRunning(true);
        await loadActiveDemos();
      }
    } catch (error) {
      console.error('Error starting demo engine:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopDemoEngine = async () => {
    try {
      setLoading(true);
      const data = await getJsonWithRetry<any>(getApiUrl('/api/demo/stop-engine'), { method: 'POST' }, { retries: 2, backoffMs: 300, maxBackoffMs: 2000, timeoutMs: 5000 });
      if (data?.success) {
        setEngineRunning(false);
      }
    } catch (error) {
      console.error('Error stopping demo engine:', error);
    } finally {
      setLoading(false);
    }
  };

  const createDemo = async () => {
    try {
      setLoading(true);
      const data = await getJsonWithRetry<any>(getApiUrl('/api/demo/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(demoForm)
      }, { retries: 3, backoffMs: 400, maxBackoffMs: 4000, timeoutMs: 7000 });
      if (data?.success) {
        setShowCreateDialog(false);
        setDemoForm({ investor_name: '', investor_email: '', investment_amount: 1000 });
        await loadActiveDemos();
        if (!engineRunning) {
          await startDemoEngine();
        }
      }
    } catch (error) {
      console.error('Error creating demo:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getSelectedTier = () => {
    return demoTiers.find(tier => tier.amount === demoForm.investment_amount);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            🚀 48-Hour Live Trading Demonstration
          </Typography>
          <Typography variant="subtitle1" sx={{ color: 'text.secondary' }}>
            Show investors real money-making capabilities with AI learning
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadActiveDemos}
            disabled={loading}
          >
            Refresh
          </Button>
          
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => setShowCreateDialog(true)}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              '&:hover': { background: 'linear-gradient(45deg, #0099cc, #007399)' }
            }}
          >
            Create Demo
          </Button>
          
          {!engineRunning ? (
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={startDemoEngine}
              disabled={loading}
              sx={{
                background: 'linear-gradient(45deg, #4caf50, #45a049)',
                '&:hover': { background: 'linear-gradient(45deg, #45a049, #3d8b40)' }
              }}
            >
              Start Engine
            </Button>
          ) : (
            <Button
              variant="contained"
              startIcon={<Stop />}
              onClick={stopDemoEngine}
              disabled={loading}
              sx={{
                background: 'linear-gradient(45deg, #f44336, #d32f2f)',
                '&:hover': { background: 'linear-gradient(45deg, #d32f2f, #b71c1c)' }
              }}
            >
              Stop Engine
            </Button>
          )}
        </Box>
      </Box>

      {/* Engine Status */}
      <Alert 
        severity={engineRunning ? 'success' : 'warning'}
        sx={{ mb: 3 }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          {engineRunning ? '🟢 DEMO ENGINE ACTIVE' : '🟡 DEMO ENGINE INACTIVE'}
        </Typography>
        <Typography variant="body2">
          {engineRunning 
            ? 'Live trading demonstrations are running with real money and AI learning'
            : 'Start the demo engine to begin live trading demonstrations'
          }
        </Typography>
      </Alert>

      {/* Investment Tiers Overview */}
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
        💎 Investment Demonstration Tiers
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {demoTiers.map((tier) => (
          <Grid item xs={12} md={6} lg={3} key={tier.amount}>
            <Card sx={{ 
              background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
              border: tier.amount === 5000 ? '2px solid #ffd700' : '1px solid #333',
              height: '100%'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <AttachMoney sx={{ color: '#00d4ff', fontSize: 24 }} />
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {formatCurrency(tier.amount)}
                  </Typography>
                  {tier.amount === 5000 && (
                    <Chip label="ELITE" size="small" sx={{ backgroundColor: '#ffd700', color: '#000' }} />
                  )}
                </Box>
                
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  {tier.name}
                </Typography>
                
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                  {tier.description}
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Target Return:</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                    {tier.target_return}%
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Risk Level:</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {tier.risk_level}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Trades/Hour:</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {tier.trades_per_hour}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Max Drawdown:</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#f44336' }}>
                    {tier.max_drawdown}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Active Demonstrations */}
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
        📊 Active Demonstrations ({activeDemos.length})
      </Typography>
      
      {activeDemos.length === 0 ? (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
              No active demonstrations
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
              Create a new demonstration to showcase live trading capabilities to investors
            </Typography>
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={() => setShowCreateDialog(true)}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                '&:hover': { background: 'linear-gradient(45deg, #0099cc, #007399)' }
              }}
            >
              Create First Demo
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {activeDemos.map((demo) => (
            <Grid item xs={12} lg={6} key={demo.demo.demo_id}>
              <Card sx={{ 
                background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
                border: '1px solid #333'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {demo.demo.investor_name}
                    </Typography>
                    <Chip
                      label={demo.is_active ? 'ACTIVE' : 'COMPLETED'}
                      size="small"
                      sx={{
                        backgroundColor: demo.is_active ? '#4caf50' : '#ff9800',
                        color: '#ffffff'
                      }}
                    />
                  </Box>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Investment Amount
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {formatCurrency(demo.demo.investment_amount)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Current Value
                      </Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontWeight: 600,
                          color: demo.demo.current_value >= demo.demo.investment_amount ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatCurrency(demo.demo.current_value)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Total Return
                      </Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontWeight: 600,
                          color: demo.demo.return_percentage >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatPercentage(demo.demo.return_percentage)}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={6}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Win Rate
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {demo.win_rate}%
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Time Remaining:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {demo.hours_remaining.toFixed(1)} hours
                      </Typography>
                    </Box>
                    
                    <LinearProgress 
                      variant="determinate" 
                      value={((48 - demo.hours_remaining) / 48) * 100}
                      sx={{ 
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha('#ffffff', 0.1),
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: '#00d4ff'
                        }
                      }}
                    />
                  </Box>
                  
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Chip
                      icon={<Psychology />}
                      label={`AI Confidence: ${(demo.demo.ai_confidence_score * 100).toFixed(1)}%`}
                      size="small"
                      sx={{ backgroundColor: '#9c27b0', color: '#ffffff' }}
                    />
                    <Chip
                      icon={<Timeline />}
                      label={`${demo.demo.trades_executed} Trades`}
                      size="small"
                      sx={{ backgroundColor: '#ff9800', color: '#ffffff' }}
                    />
                  </Box>
                  
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<TrendingUp />}
                    onClick={() => setSelectedDemo(demo)}
                    sx={{ mt: 2 }}
                  >
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Demo Dialog */}
      <Dialog 
        open={showCreateDialog} 
        onClose={() => setShowCreateDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            🚀 Create 48-Hour Live Trading Demo
          </Typography>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Investor Name"
                  value={demoForm.investor_name}
                  onChange={(e) => setDemoForm({...demoForm, investor_name: e.target.value})}
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  label="Investor Email"
                  type="email"
                  value={demoForm.investor_email}
                  onChange={(e) => setDemoForm({...demoForm, investor_email: e.target.value})}
                  sx={{ mb: 2 }}
                />
                
                <FormControl fullWidth>
                  <InputLabel>Investment Amount</InputLabel>
                  <Select
                    value={demoForm.investment_amount}
                    onChange={(e) => setDemoForm({...demoForm, investment_amount: Number(e.target.value)})}
                  >
                    {demoTiers.map((tier) => (
                      <MenuItem key={tier.amount} value={tier.amount}>
                        {formatCurrency(tier.amount)} - {tier.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                {getSelectedTier() && (
                  <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                        {getSelectedTier()?.name}
                      </Typography>
                      
                      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                        {getSelectedTier()?.description}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Target Return:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                          {getSelectedTier()?.target_return}%
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Risk Level:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {getSelectedTier()?.risk_level}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Trades per Hour:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {getSelectedTier()?.trades_per_hour}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setShowCreateDialog(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={createDemo}
            disabled={loading || !demoForm.investor_name || !demoForm.investor_email}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              '&:hover': { background: 'linear-gradient(45deg, #0099cc, #007399)' }
            }}
          >
            {loading ? 'Creating...' : 'Create Demo'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Demo Details Dialog */}
      <Dialog
        open={!!selectedDemo}
        onClose={() => setSelectedDemo(null)}
        maxWidth="lg"
        fullWidth
      >
        {selectedDemo && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  📊 {selectedDemo.demo.investor_name} - Live Demo Details
                </Typography>
                <Button onClick={() => setSelectedDemo(null)}>
                  <Close />
                </Button>
              </Box>
            </DialogTitle>

            <DialogContent>
              {/* Performance Overview */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <AttachMoney sx={{ color: '#00d4ff', fontSize: 32, mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                        {formatCurrency(selectedDemo.demo.current_value)}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Current Value
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <TrendingUp sx={{
                        color: selectedDemo.demo.return_percentage >= 0 ? '#4caf50' : '#f44336',
                        fontSize: 32, mb: 1
                      }} />
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 700,
                          color: selectedDemo.demo.return_percentage >= 0 ? '#4caf50' : '#f44336'
                        }}
                      >
                        {formatPercentage(selectedDemo.demo.return_percentage)}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Total Return
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Psychology sx={{ color: '#9c27b0', fontSize: 32, mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: '#9c27b0' }}>
                        {(selectedDemo.demo.ai_confidence_score * 100).toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        AI Confidence
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                  <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Timeline sx={{ color: '#ff9800', fontSize: 32, mb: 1 }} />
                      <Typography variant="h5" sx={{ fontWeight: 700, color: '#ff9800' }}>
                        {selectedDemo.win_rate}%
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Win Rate
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Time Progress */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    ⏱️ Demo Progress
                  </Typography>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      Time Elapsed: {selectedDemo.hours_elapsed} hours
                    </Typography>
                    <Typography variant="body2">
                      Time Remaining: {selectedDemo.hours_remaining.toFixed(1)} hours
                    </Typography>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={((48 - selectedDemo.hours_remaining) / 48) * 100}
                    sx={{
                      height: 12,
                      borderRadius: 6,
                      backgroundColor: alpha('#ffffff', 0.1),
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: '#00d4ff'
                      }
                    }}
                  />
                </CardContent>
              </Card>

              {/* Recent Trades */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    📈 Recent Trades
                  </Typography>

                  <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Symbol</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Entry</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Exit</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>P&L</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>AI Confidence</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedDemo.recent_trades?.slice(0, 5).map((trade: any, index: number) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {trade.symbol}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={trade.trade_type.toUpperCase()}
                                size="small"
                                sx={{
                                  backgroundColor: trade.trade_type === 'buy' ? '#4caf50' : '#f44336',
                                  color: '#ffffff'
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                ${trade.entry_price.toFixed(2)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                ${trade.exit_price.toFixed(2)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontWeight: 600,
                                  color: trade.profit_loss >= 0 ? '#4caf50' : '#f44336'
                                }}
                              >
                                {formatCurrency(trade.profit_loss)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {(trade.ai_confidence * 100).toFixed(1)}%
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>

              {/* AI Learning Progress */}
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    🤖 AI Learning Progress
                  </Typography>

                  {selectedDemo.learning_metrics?.slice(0, 3).map((metric: any, index: number) => (
                    <Box key={index} sx={{ mb: 2, p: 2, backgroundColor: alpha('#ffffff', 0.05), borderRadius: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          Learning Iteration #{metric.learning_iteration}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {new Date(metric.timestamp).toLocaleTimeString()}
                        </Typography>
                      </Box>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Strategy Adaptation:</strong> {metric.strategy_adaptation}
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Market Insight:</strong> {metric.market_insight}
                      </Typography>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">
                          <strong>Confidence Level:</strong> {(metric.confidence_level * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#4caf50' }}>
                          <strong>Improvement:</strong> +{(metric.accuracy_improvement * 100).toFixed(2)}%
                        </Typography>
                      </Box>

                      {index < selectedDemo.learning_metrics.length - 1 && <Divider sx={{ mt: 2 }} />}
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </DialogContent>
          </>
        )}
      </Dialog>

      {loading && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  );
};

export default InvestorDemoLauncher;
