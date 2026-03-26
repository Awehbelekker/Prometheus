import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  Security,
  Warning,
  CheckCircle,
  Schedule
} from '@mui/icons-material';
import { useTradingMode, TradingMode } from '../contexts/TradingModeContext';

const TradingModeSelector: React.FC = () => {
  const {
    tradingMode,
    switchTradingMode,
    isLiveTrading,
    isPaperTrading,
    isDemoMode,
    canSwitchToLive,
    userTier,
    accountBalance
  } = useTradingMode();

  const [showModeDialog, setShowModeDialog] = useState(false);
  const [selectedMode, setSelectedMode] = useState<TradingMode>(tradingMode);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeSwitch = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const success = await switchTradingMode(selectedMode);
      if (success) {
        setShowModeDialog(false);
      } else {
        setError('Failed to switch trading mode. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const getModeColor = (mode: TradingMode) => {
    switch (mode) {
      case 'live': return '#f44336';
      case 'paper': return '#2196f3';
      case 'demo': return '#ff9800';
      default: return '#666';
    }
  };

  const getModeIcon = (mode: TradingMode) => {
    switch (mode) {
      case 'live': return <AccountBalance />;
      case 'paper': return <TrendingUp />;
      case 'demo': return <Schedule />;
      default: return <Security />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <Box>
      {/* Current Mode Display */}
      <Card sx={{ 
        background: `linear-gradient(135deg, ${getModeColor(tradingMode)}20, ${getModeColor(tradingMode)}10)`,
        border: `1px solid ${getModeColor(tradingMode)}`,
        mb: 2
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {getModeIcon(tradingMode)}
              <Box>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  {tradingMode.toUpperCase()} TRADING MODE
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa' }}>
                  Balance: {formatCurrency(accountBalance[tradingMode])}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {isLiveTrading && (
                <Chip
                  label="🔴 LIVE MONEY"
                  sx={{
                    backgroundColor: '#f44336',
                    color: 'white',
                    fontWeight: 700,
                    animation: 'pulse 2s infinite'
                  }}
                />
              )}
              {isPaperTrading && (
                <Chip
                  label="📊 VIRTUAL MONEY"
                  sx={{
                    backgroundColor: '#2196f3',
                    color: 'white',
                    fontWeight: 600
                  }}
                />
              )}
              {isDemoMode && (
                <Chip
                  label="⏱️ 48H DEMO"
                  sx={{
                    backgroundColor: '#ff9800',
                    color: 'white',
                    fontWeight: 600
                  }}
                />
              )}
              
              <Button
                variant="outlined"
                onClick={() => setShowModeDialog(true)}
                sx={{
                  borderColor: getModeColor(tradingMode),
                  color: getModeColor(tradingMode),
                  '&:hover': {
                    backgroundColor: `${getModeColor(tradingMode)}20`
                  }
                }}
              >
                Switch Mode
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Mode Switch Dialog */}
      <Dialog
        open={showModeDialog}
        onClose={() => setShowModeDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white'
          }
        }}
      >
        <DialogTitle>
          <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 700 }}>
            Select Trading Mode
          </Typography>
        </DialogTitle>

        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Paper Trading */}
            <Grid item xs={12} md={4}>
              <Card
                sx={{
                  background: selectedMode === 'paper' ? 'rgba(33, 150, 243, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: selectedMode === 'paper' ? '2px solid #2196f3' : '1px solid rgba(255, 255, 255, 0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'rgba(33, 150, 243, 0.1)'
                  }
                }}
                onClick={() => setSelectedMode('paper')}
              >
                <CardContent>
                  <Box sx={{ textAlign: 'center' }}>
                    <TrendingUp sx={{ fontSize: 40, color: '#2196f3', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Paper Trading
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                      Practice with virtual money
                    </Typography>
                    <Typography variant="h6" sx={{ color: '#2196f3' }}>
                      {formatCurrency(accountBalance.paper)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Virtual Balance
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Live Trading */}
            <Grid item xs={12} md={4}>
              <Card
                sx={{
                  background: selectedMode === 'live' ? 'rgba(244, 67, 54, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: selectedMode === 'live' ? '2px solid #f44336' : '1px solid rgba(255, 255, 255, 0.1)',
                  cursor: canSwitchToLive ? 'pointer' : 'not-allowed',
                  opacity: canSwitchToLive ? 1 : 0.5,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: canSwitchToLive ? 'rgba(244, 67, 54, 0.1)' : undefined
                  }
                }}
                onClick={() => canSwitchToLive && setSelectedMode('live')}
              >
                <CardContent>
                  <Box sx={{ textAlign: 'center' }}>
                    <AccountBalance sx={{ fontSize: 40, color: '#f44336', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Live Trading
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                      Trade with real money
                    </Typography>
                    <Typography variant="h6" sx={{ color: '#f44336' }}>
                      {formatCurrency(accountBalance.live)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Real Balance
                    </Typography>
                    {!canSwitchToLive && (
                      <Chip
                        label="Premium Required"
                        size="small"
                        sx={{
                          mt: 1,
                          backgroundColor: '#ff9800',
                          color: 'white'
                        }}
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Demo Mode */}
            <Grid item xs={12} md={4}>
              <Card
                sx={{
                  background: selectedMode === 'demo' ? 'rgba(255, 152, 0, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: selectedMode === 'demo' ? '2px solid #ff9800' : '1px solid rgba(255, 255, 255, 0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'rgba(255, 152, 0, 0.1)'
                  }
                }}
                onClick={() => setSelectedMode('demo')}
              >
                <CardContent>
                  <Box sx={{ textAlign: 'center' }}>
                    <Schedule sx={{ fontSize: 40, color: '#ff9800', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      48-Hour Demo
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                      Limited time trial
                    </Typography>
                    <Typography variant="h6" sx={{ color: '#ff9800' }}>
                      {formatCurrency(accountBalance.demo)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Demo Balance
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Warning for Live Trading */}
          {selectedMode === 'live' && (
            <Alert severity="warning" sx={{ mt: 3 }}>
              <Typography variant="body2">
                ⚠️ <strong>WARNING:</strong> Live trading uses real money. All trades will be executed with actual funds. 
                Make sure you understand the risks involved.
              </Typography>
            </Alert>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setShowModeDialog(false)} sx={{ color: '#aaa' }}>
            Cancel
          </Button>
          <Button
            onClick={handleModeSwitch}
            variant="contained"
            disabled={isLoading || selectedMode === tradingMode}
            sx={{
              background: `linear-gradient(45deg, ${getModeColor(selectedMode)}, ${getModeColor(selectedMode)}cc)`
            }}
          >
            {isLoading ? 'Switching...' : `Switch to ${selectedMode.toUpperCase()}`}
          </Button>
        </DialogActions>
      </Dialog>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </Box>
  );
};

export default TradingModeSelector;
