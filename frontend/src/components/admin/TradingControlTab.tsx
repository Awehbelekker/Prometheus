import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Divider,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Warning as Emergency,
  Settings,
  Speed,
  Security,
  TrendingUp,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';

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

interface TradingControlTabProps {
  tradingEngineActive: boolean;
  onToggleEngine: () => void;
  platformStats: PlatformStats;
  formatCurrency: (amount: number) => string;
  formatPercentage: (value: number) => string;
}

const TradingControlTab: React.FC<TradingControlTabProps> = ({
  tradingEngineActive,
  onToggleEngine,
  platformStats,
  formatCurrency,
  formatPercentage
}) => {
  const [emergencyStopDialog, setEmergencyStopDialog] = useState(false);
  const [riskLimitsDialog, setRiskLimitsDialog] = useState(false);
  const [dryRunMode, setDryRunMode] = useState(false);
  const [maxDailyLoss, setMaxDailyLoss] = useState('5000');
  const [maxPositionSize, setMaxPositionSize] = useState('2');

  const handleEmergencyStop = () => {
    setEmergencyStopDialog(false);
    onToggleEngine();
    // In real app, this would trigger emergency stop API
  };

  const engineStatus = tradingEngineActive ? 'active' : 'inactive';
  const statusColor = tradingEngineActive ? '#4caf50' : '#f44336';
  const statusIcon = tradingEngineActive ? <CheckCircle /> : <Error />;

  return (
    <Box>
      <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
        🎛️ Trading Engine Control Center
      </Typography>

      {/* Engine Status Card */}
      <Card sx={{ 
        background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)',
        border: `2px solid ${statusColor}`,
        mb: 3
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ color: statusColor, fontSize: 32 }}>
                {statusIcon}
              </Box>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 700, color: statusColor }}>
                  Trading Engine {engineStatus.toUpperCase()}
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  {tradingEngineActive 
                    ? 'Revolutionary engines are actively trading' 
                    : 'All trading engines are stopped'
                  }
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant={tradingEngineActive ? "outlined" : "contained"}
                color={tradingEngineActive ? "error" : "success"}
                size="large"
                startIcon={tradingEngineActive ? <Stop /> : <PlayArrow />}
                onClick={onToggleEngine}
                sx={{ minWidth: 150 }}
              >
                {tradingEngineActive ? 'Stop Trading' : 'Start Trading'}
              </Button>
              
              <Button
                variant="outlined"
                color="error"
                startIcon={<Emergency />}
                onClick={() => setEmergencyStopDialog(true)}
                disabled={!tradingEngineActive}
              >
                Emergency Stop
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Trading Controls Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                🛡️ Safety Controls
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={dryRunMode}
                      onChange={(e) => setDryRunMode(e.target.checked)}
                      color="warning"
                    />
                  }
                  label="DRY-RUN Mode (Safe Testing)"
                />
                
                <FormControlLabel
                  control={<Switch defaultChecked color="success" />}
                  label="Circuit Breakers Enabled"
                />
                
                <FormControlLabel
                  control={<Switch defaultChecked color="info" />}
                  label="Market Hours Only"
                />
                
                <FormControlLabel
                  control={<Switch defaultChecked color="primary" />}
                  label="Risk Limits Active"
                />
                
                <Button
                  variant="outlined"
                  startIcon={<Settings />}
                  onClick={() => setRiskLimitsDialog(true)}
                  sx={{ alignSelf: 'flex-start' }}
                >
                  Configure Risk Limits
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                📊 Live Performance Metrics
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Daily P&L</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#4caf50' }}>
                      {formatCurrency(platformStats.dailyPnL)}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={75}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255,255,255,0.1)',
                      '& .MuiLinearProgress-bar': { bgcolor: '#4caf50' }
                    }}
                  />
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Success Rate</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#00d4ff' }}>
                      {formatPercentage(platformStats.successRate)}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={platformStats.successRate}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255,255,255,0.1)',
                      '& .MuiLinearProgress-bar': { bgcolor: '#00d4ff' }
                    }}
                  />
                </Box>
                
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Risk Utilization</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#ff9800' }}>
                      45%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={45}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255,255,255,0.1)',
                      '& .MuiLinearProgress-bar': { bgcolor: '#ff9800' }
                    }}
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Revolutionary Engines Status */}
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            🚀 Revolutionary Trading Engines Status
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6} lg={3}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(42, 42, 42, 0.5)' }}>
                <Chip
                  label="CRYPTO ENGINE"
                  color={tradingEngineActive ? "success" : "default"}
                  sx={{ mb: 1, fontWeight: 600 }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  24/7 Arbitrage & Grid Trading
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(42, 42, 42, 0.5)' }}>
                <Chip
                  label="OPTIONS ENGINE"
                  color={tradingEngineActive ? "success" : "default"}
                  sx={{ mb: 1, fontWeight: 600 }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Iron Condors & Butterflies
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(42, 42, 42, 0.5)' }}>
                <Chip
                  label="MARKET MAKER"
                  color={tradingEngineActive ? "success" : "default"}
                  sx={{ mb: 1, fontWeight: 600 }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Spread Capture & Liquidity
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6} lg={3}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'rgba(42, 42, 42, 0.5)' }}>
                <Chip
                  label="ADVANCED ENGINE"
                  color={tradingEngineActive ? "success" : "default"}
                  sx={{ mb: 1, fontWeight: 600 }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  VWAP & Smart Routing
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Emergency Stop Dialog */}
      <Dialog open={emergencyStopDialog} onClose={() => setEmergencyStopDialog(false)}>
        <DialogTitle sx={{ color: '#f44336' }}>
          🚨 Emergency Stop Confirmation
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This will immediately halt ALL trading engines and close any open positions.
            This action cannot be undone and may result in losses.
          </Alert>
          <Typography variant="body2">
            Are you sure you want to execute an emergency stop?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmergencyStopDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleEmergencyStop}
            color="error"
            variant="contained"
            startIcon={<Emergency />}
          >
            EMERGENCY STOP
          </Button>
        </DialogActions>
      </Dialog>

      {/* Risk Limits Dialog */}
      <Dialog open={riskLimitsDialog} onClose={() => setRiskLimitsDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>⚙️ Configure Risk Limits</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              fullWidth
              label="Maximum Daily Loss ($)"
              type="number"
              value={maxDailyLoss}
              onChange={(e) => setMaxDailyLoss(e.target.value)}
            />
            <TextField
              fullWidth
              label="Maximum Position Size (%)"
              type="number"
              value={maxPositionSize}
              onChange={(e) => setMaxPositionSize(e.target.value)}
            />
            <Alert severity="info">
              These limits will be applied to all trading engines to ensure safe operation.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRiskLimitsDialog(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<Settings />}>
            Save Limits
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TradingControlTab;
