import React, { useState, useEffect, useMemo, useCallback, memo } from 'react';
import { liveMarketData, LiveAnalytics, PortfolioPosition, TradingSignal } from '../services/LiveMarketData';
import { paperMarketData } from '../services/PaperMarketData';
import { realAlpacaService, RealTradingData } from '../services/RealAlpacaService';
import RealTimeWealthTracker from './RealTimeWealthTracker';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Stack,
  Grid,
  LinearProgress,
  alpha,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Tooltip,
  Fade,
  Grow,
  Slide,
  Badge,
  Avatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  ShowChart,
  PlayArrow,
  Pause,
  Timer,
  School,
  CheckCircle,
  Star,
  Lightbulb,
  AttachMoney,
  Timeline,
  Speed,
  Assessment,
  TrendingDown,
  BarChart,
  PieChart,
  Insights,
  AutoGraph,
  Analytics
} from '@mui/icons-material';
import { apiCall, API_ENDPOINTS } from '../config/api';
import { useSnackbar } from 'notistack';
import ConfirmDialog from './common/ConfirmDialog';

// Removed demo components: TrialStatusChip, TrialSummaryCard, RoiAllocationPanel
import { useTradingMode } from '../contexts/TradingModeContext';
import TradingModeSelector from './TradingModeSelector';
import OrderManagement from './OrderManagement';

interface TradingDashboardProps {
    mode?: 'live' | 'paper';
    user?: any;
    showGamification?: boolean;
    enableSocialFeatures?: boolean;
    requiresFundAllocation?: boolean;
    showRiskControls?: boolean;
}

// Enhanced Mini Chart Component
const MiniChart: React.FC<{ data: number[], color: string, label: string }> = ({ data, color, label }) => {
  const [animatedData, setAnimatedData] = useState<number[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedData(data), 100);
    return () => clearTimeout(timer);
  }, [data]);

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = animatedData.map((value, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((value - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <Box sx={{ position: 'relative', height: 60, width: '100%' }}>
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id={`gradient-${label}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.05" />
          </linearGradient>
        </defs>
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2"
          points={points}
          style={{
            filter: 'drop-shadow(0 0 4px rgba(0,212,255,0.3))',
            transition: 'all 0.3s ease'
          }}
        />
        <polygon
          fill={`url(#gradient-${label})`}
          points={`0,100 ${points} 100,100`}
        />
      </svg>
    </Box>
  );
};

// Circular Progress Indicator
const CircularProgressIndicator: React.FC<{
  value: number,
  max: number,
  color: string,
  label: string,
  size?: number
}> = ({ value, max, color, label, size = 80 }) => {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 200);
    return () => clearTimeout(timer);
  }, [value]);

  const percentage = (animatedValue / max) * 100;

  return (
    <Box sx={{ position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}>
      <CircularProgress
        variant="determinate"
        value={percentage}
        size={size}
        thickness={4}
        sx={{
          color: color,
          '& .MuiCircularProgress-circle': {
            strokeLinecap: 'round',
            filter: `drop-shadow(0 0 6px ${color}40)`
          }
        }}
      />
      <Box sx={{
        position: 'absolute',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography variant="h6" sx={{ color: 'white', fontWeight: 700, fontSize: '0.9rem' }}>
          {percentage.toFixed(1)}%
        </Typography>
        <Typography variant="caption" sx={{ color: '#aaa', fontSize: '0.7rem' }}>
          {label}
        </Typography>
      </Box>
    </Box>
  );
};

/**
 * 🚀 ENHANCED TRADING DASHBOARD
 * Complete trading interface with 48-hour trial showcase and investment guidance
 */
const TradingDashboard: React.FC<TradingDashboardProps> = ({ mode }) => {
  const [isActive, setIsActive] = useState(false);
  const [liveAnalytics, setLiveAnalytics] = useState<LiveAnalytics | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioPosition[]>([]);
  const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
  const [realTradingData, setRealTradingData] = useState<RealTradingData | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedTimePeriod, setSelectedTimePeriod] = useState<'24h' | '48h' | '7d' | '1m'>('24h');
  const [projectionData, setProjectionData] = useState<any>(null);
  const [isLoadingRealData, setIsLoadingRealData] = useState(false);

  // Paper Trading Session State
  const [sessionDialog, setSessionDialog] = useState(false);
  const [sessionType, setSessionType] = useState('24_hour');
  const [startingCapital, setStartingCapital] = useState('10000');
  const [customHours, setCustomHours] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState<null | 'start' | 'stop'>(null);
  const { enqueueSnackbar } = useSnackbar();

  const [activeSession, setActiveSession] = useState<any>(null);
  const [userProgress, setUserProgress] = useState<any>(null);

  // Use trading mode context for live data distinction
  const {
    tradingMode,
    isLiveTrading,
    isPaperTrading,
    isDemoMode,
    accountBalance
  } = useTradingMode();

  // Determine the effective mode for this dashboard instance:
  // - If a `mode` prop is provided (e.g., separate Live vs Paper tabs), use it.
  // - Otherwise, fall back to the global context mode.
  const effectiveMode = mode ?? tradingMode;
  const isLiveView = effectiveMode === 'live';
  const isPaperView = effectiveMode === 'paper';
  const isDemoView = effectiveMode === 'demo';
  const currentPortfolioValue = accountBalance[effectiveMode as keyof typeof accountBalance];

  // Paper Trading Session Functions
  const handleCreateSession = async () => {
    try {
      const result = await apiCall('/api/user/create-session', {
        method: 'POST',
        headers: { 'X-User-ID': 'user_demo_001' },
        body: JSON.stringify({
          session_type: sessionType,
          starting_capital: parseFloat(startingCapital),
          custom_hours: sessionType === 'custom' ? parseInt(customHours) : undefined
        })
      });
      setSessionDialog(false);
      await loadUserDashboard();
      console.log('✅ Paper trading session created:', result.session_id);
    } catch (error) {
      console.error('❌ Failed to create session:', error);
    }
  };

  const loadUserDashboard = async () => {
    try {
      const data = await apiCall('/api/user/dashboard', {
        headers: { 'X-User-ID': 'user_demo_001' }
      });
      setActiveSession(data.active_sessions?.[0] || null);
      setUserProgress(data);
    } catch (error) {
      console.error('❌ Failed to load user dashboard:', error);
    }
  };

  // Load user dashboard on component mount
  useEffect(() => {
    if (isPaperView) {
      loadUserDashboard();
    }
  }, [isPaperView]);

  // Handler for Start/Stop Trading button
  const handleTradingToggle = async () => {
    try {
      if (!isActive) {
        // Starting trading
        console.log(`🚀 Starting ${effectiveMode} trading...`);

        // Call backend to start trading session
        await apiCall(API_ENDPOINTS.START_TRADING, {
          method: 'POST',
          body: JSON.stringify({
            mode: effectiveMode,
            auto_trading: true
          })
        });
        setIsActive(true);
        console.log('✅ Trading started successfully');
        enqueueSnackbar('Trading started', { variant: 'success' });
        // Refresh trading data after starting
        loadRealTradingData();
      } else {
        // Stopping trading
        console.log('⏸️ Stopping trading...');
        setIsActive(false);
        enqueueSnackbar('Trading stopped', { variant: 'info' });
        console.log('✅ Trading stopped');
      }
    } catch (error) {
      console.error('❌ Error toggling trading:', error);
    }
  };

  // Load real Alpaca trading data function
  const loadRealTradingData = async () => {
    if (isDemoView) return; // Skip real data for demo mode

    setIsLoadingRealData(true);
    try {
      console.log(`🔍 Loading real ${effectiveMode} trading data...`);
      const realData = await realAlpacaService.getTradingData(effectiveMode as 'paper' | 'live');

      setRealTradingData(realData);
      setLiveAnalytics(realData.analytics);

      console.log('✅ Real trading data loaded:', {
        mode: effectiveMode,
        portfolio_value: realData.paperAccount.portfolio_value + realData.liveAccount.portfolio_value,
        positions: realData.paperPositions.length + realData.livePositions.length,
        orders: realData.paperOrders.length + realData.liveOrders.length
      });
    } catch (error) {
      console.error('❌ Failed to load real trading data:', error);
      // Fallback to demo data if real data fails
      console.log('🔄 Falling back to demo market data...');
    } finally {
      setIsLoadingRealData(false);
    }
  };

  // Load real Alpaca trading data instead of demo data
  useEffect(() => {
    loadRealTradingData();

    // Refresh real data every 30 seconds
    const interval = setInterval(loadRealTradingData, 30000);
    return () => clearInterval(interval);
  }, [effectiveMode, isDemoView]);

  // Connect to the appropriate market data stream (live vs paper) - only for demo mode
  useEffect(() => {
    if (!isDemoView) return; // Only use demo market data for demo mode

    const source = isLiveView ? liveMarketData : paperMarketData;
    const subscriptionId = source.subscribe((data) => {
      if (data.type === 'initial' || data.type === 'update') {
        setLiveAnalytics(data.analytics);
        setPortfolio(data.portfolio);
        if (data.signals) {
          setTradingSignals(data.signals);
        }
      }
    });

    return () => {
      source.unsubscribe(subscriptionId);
    };
  }, [isLiveView, isDemoView]);

  // Remove demo endpoints - we now use only real Alpaca data
  // No more trial status, ROI allocation, or other demo data fetching

  // Real trading mode - no demo countdown needed

  // Get current values from live data or defaults
  const displayPortfolioValue = liveAnalytics?.portfolioValue ?? currentPortfolioValue;
  const dailyPnL = liveAnalytics?.dailyPnL ?? 0;
  const totalTrades = liveAnalytics?.totalTrades ?? 0;

  // Investment guidance steps
  const investmentSteps = [
    'Start with Paper Trading',
    'Learn Risk Management',
    'Develop Your Strategy',
    'Upgrade to Live Trading'
  ];

  // Investment recommendations
  const investmentRecommendations = [
    {
      title: 'Conservative Portfolio',
      description: 'Low risk, steady returns for beginners',
      allocation: '60% Stocks, 30% Bonds, 10% Cash',
      expectedReturn: '6-8% annually',
      riskLevel: 'Low',
      color: '#4caf50'
    },
    {
      title: 'Balanced Growth',
      description: 'Moderate risk with growth potential',
      allocation: '70% Stocks, 20% Bonds, 10% Alternatives',
      expectedReturn: '8-12% annually',
      riskLevel: 'Medium',
      color: '#ff9800'
    },
    {
      title: 'Aggressive Growth',
      description: 'High risk, high reward for experienced traders',
      allocation: '85% Stocks, 10% Alternatives, 5% Cash',
      expectedReturn: '12-18% annually',
      riskLevel: 'High',
      color: '#f44336'
    }
  ];

  // Currency formatter to avoid duplicate symbols like "$+$" and handle signs cleanly
  const formatCurrency = (n: number, opts: Intl.NumberFormatOptions = {}) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2, ...opts }).format(n);
  const formatCurrencySigned = (n: number) => {
    const formatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(Math.abs(n));
    return n >= 0 ? `+${formatted}` : `-${formatted}`;
  };

  // Calculate investment outcome projections
  const calculateProjection = (timePeriod: '24h' | '48h' | '7d' | '1m') => {
    const baseReturn = liveAnalytics?.avgTradeReturn || 2.5; // Default 2.5% average
    const volatility = liveAnalytics?.volatility || 15; // Default 15% volatility
    const currentValue = displayPortfolioValue;

    let multiplier = 1;
    let riskFactor = 1;

    switch (timePeriod) {
      case '24h':
        multiplier = 1;
        riskFactor = 0.5;
        break;
      case '48h':
        multiplier = 2;
        riskFactor = 0.7;
        break;
      case '7d':
        multiplier = 7;
        riskFactor = 1.2;
        break;
      case '1m':
        multiplier = 30;
        riskFactor = 2.0;
        break;
    }

    const projectedReturn = (baseReturn * multiplier * riskFactor) / 100;
    const projectedValue = currentValue * (1 + projectedReturn);
    const projectedProfit = projectedValue - currentValue;
    const projectedRisk = volatility * riskFactor;

    return {
      projectedValue,
      projectedProfit,
      projectedReturn: projectedReturn * 100,
      projectedRisk,
      timePeriod
    };
  };

  // Handle time period selection
  const handleTimePeriodChange = (period: '24h' | '48h' | '7d' | '1m') => {
    setSelectedTimePeriod(period);
    setProjectionData(calculateProjection(period));
  };

  // Initialize projection data on component mount
  useEffect(() => {
    if (liveAnalytics) {
      setProjectionData(calculateProjection(selectedTimePeriod));
    }
  }, [liveAnalytics, displayPortfolioValue]);

  return (
    <Box sx={{
      p: 3,
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
      color: 'white',
      '& @keyframes pulse': {
        '0%': { opacity: 1, transform: 'scale(1)' },
        '50%': { opacity: 0.8, transform: 'scale(1.02)' },
        '100%': { opacity: 1, transform: 'scale(1)' }
      },
      '& @keyframes shimmer': {
        '0%': { backgroundPosition: '200% 0' },
        '100%': { backgroundPosition: '-200% 0' }
      },
      '& @keyframes gradientShift': {
        '0%': { backgroundPosition: '0% 50%' },
        '50%': { backgroundPosition: '100% 50%' },
        '100%': { backgroundPosition: '0% 50%' }
      },
      '& @keyframes slideInUp': {
        '0%': { transform: 'translateY(30px)', opacity: 0 },
        '100%': { transform: 'translateY(0)', opacity: 1 }
      },
      '& @keyframes fadeInScale': {
        '0%': { transform: 'scale(0.95)', opacity: 0 },
        '100%': { transform: 'scale(1)', opacity: 1 }
      },
      '& @keyframes glow': {
        '0%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.3)' },
        '50%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.6)' },
        '100%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.3)' }
      }
    }}>
      {/* Enhanced Header with Staggered Animations */}
      <Fade in={true} timeout={600}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Grow in={true} timeout={800}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {isLiveView ? <AccountBalance sx={{ color: '#00d4ff', fontSize: 32 }} /> : <ShowChart sx={{ color: '#00d4ff', fontSize: 32 }} />}
              </Box>
            </Grow>
            <Typography variant="h4" sx={{
              fontWeight: 700,
              background: 'linear-gradient(45deg, #00d4ff, #ffffff)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              animation: 'fadeInScale 0.8s ease-out'
            }}>
              {isLiveView ? 'Live Trading Dashboard' : isDemoView ? '48-Hour Demo Trading' : 'Paper Trading'}
            </Typography>
          </Box>
          <Slide in={true} direction="left" timeout={1000}>
            <Chip
              label={isLiveView ? 'LIVE MONEY' : isDemoView ? 'DEMO TRIAL' : 'PAPER TRADING'}
              color={isLiveView ? 'error' : isDemoView ? 'warning' : 'info'}
              sx={{
                fontWeight: 600,
                fontSize: '0.8rem',
                animation: isDemoView ? 'pulse 2s infinite' : 'none',
                boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)'
              }}
            />
          </Slide>

          {/* Paper Trading Session Controls */}
          {isPaperView && (
            <>
              {activeSession ? (
                <Slide in={true} direction="left" timeout={1200}>
                  <Chip
                    icon={<Timer />}
                    label={`Active Session: ${activeSession.session_type.replace('_', ' ')} - ${activeSession.time_remaining_hours?.toFixed(1) || 0}h left`}
                    sx={{
                      backgroundColor: '#4caf50',
                      color: 'white',
                      fontWeight: 600,
                      boxShadow: '0 4px 15px rgba(76, 175, 80, 0.3)'
                    }}
                  />
                </Slide>
              ) : (
                <Slide in={true} direction="left" timeout={1200}>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={() => setSessionDialog(true)}
                    sx={{
                      background: 'linear-gradient(45deg, #00d4ff 30%, #0099cc 90%)',
                      fontWeight: 600,
                      boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #0099cc 30%, #00d4ff 90%)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 20px rgba(0, 212, 255, 0.4)'
                      }
                    }}
                  >
                    Start Paper Session
                  </Button>
                </Slide>
              )}

              {userProgress && (
                <Slide in={true} direction="left" timeout={1400}>
                  <Chip
                    icon={<Star />}
                    label={`Level ${userProgress.current_level} • ${userProgress.total_achievements} Achievements`}
                    sx={{
                      backgroundColor: '#ff9800',
                      color: 'white',
                      fontWeight: 600,
                      boxShadow: '0 4px 15px rgba(255, 152, 0, 0.3)'
                    }}
                  />
                </Slide>
              )}
            </>
          )}

          {realTradingData && (
            <>
              <Slide in={true} direction="left" timeout={1200}>
                <Chip
                  icon={<Timer />}
                  label={`Real Trading: ${realTradingData.analytics.totalTrades} trades`}
                  sx={{
                    backgroundColor: '#00d4ff',
                    color: 'white',
                    fontWeight: 600,
                    animation: 'none',
                    boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)'
                  }}
                />
              </Slide>
              <Fade in={true} timeout={1400}>
                <Box>
                  {/* Real Trading Status - No more demo trial status */}
                  {realTradingData && (
                    <div style={{
                      padding: '12px',
                      backgroundColor: 'rgba(0, 212, 255, 0.1)',
                      borderRadius: '8px',
                      border: '1px solid rgba(0, 212, 255, 0.3)'
                    }}>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: '#00d4ff' }}>
                        Real Trading Active - P&L: ${realTradingData.analytics.todaysPnL.toFixed(2)}
                      </span>
                    </div>
                  )}
                </Box>
              </Fade>
            </>
          )}
        </Stack>
      </Fade>

      {/* Enhanced KPI Cards with Staggered Animations */}

      <ConfirmDialog
        open={confirmOpen}
        title={confirmAction === 'start' ? (isLiveView ? 'Start LIVE trading?' : 'Start paper trading?') : 'Stop trading?'}
        description={confirmAction === 'start' ? (isLiveView ? 'You are about to start live trading with real funds.' : 'You are about to start a paper trading session.') : 'You are about to stop the current trading session.'}
        confirmLabel={confirmAction === 'start' ? 'Start' : 'Stop'}
        confirmColor={confirmAction === 'start' ? 'success' : 'error'}
        onConfirm={async () => { setConfirmOpen(false); await handleTradingToggle(); setConfirmAction(null); }}
        onClose={() => setConfirmOpen(false)}
      />

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Grow in={true} timeout={800}>
            <Card sx={{
              background: `linear-gradient(135deg, ${alpha('#00d4ff', 0.15)} 0%, ${alpha('#00d4ff', 0.05)} 100%)`,
              border: `2px solid ${alpha('#00d4ff', 0.4)}`,
              backdropFilter: 'blur(15px)',
              borderRadius: 3,
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden',
              '&:hover': {



                transform: 'translateY(-8px) scale(1.02)',
                boxShadow: '0 12px 30px rgba(0, 212, 255, 0.3)',
                border: `2px solid #00d4ff`
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '3px',
                background: 'linear-gradient(90deg, #00d4ff, #4caf50, #00d4ff)',
                backgroundSize: '200% 100%',
                animation: 'shimmer 3s linear infinite'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                    Portfolio Value
                  </Typography>
                  <AccountBalance sx={{ color: '#00d4ff', fontSize: 28 }} />
                </Box>
                <Typography variant="h3" sx={{
                  fontWeight: 800,
                  color: 'white',
                  mb: 1,
                  textShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
                }}>
                  {formatCurrency(displayPortfolioValue)}
                </Typography>
                <Typography variant="caption" sx={{
                  color: '#aaa',
                  fontWeight: 500,
                  letterSpacing: '0.5px'
                }}>
                  {isLiveView ? 'Real Money' : isDemoView ? 'Demo Money' : 'Virtual Money'}
                </Typography>
              </CardContent>
            </Card>
          </Grow>
        </Grid>

        {/* Enhanced Trading Controls */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.95) 0%, rgba(0, 212, 255, 0.05) 100%)',
            border: '2px solid rgba(0, 212, 255, 0.4)',
            borderRadius: 4,
            backdropFilter: 'blur(15px)',
            boxShadow: '0 8px 32px rgba(0, 212, 255, 0.2)',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '3px',
              background: 'linear-gradient(90deg, #00d4ff, #4caf50, #ff9800, #00d4ff)',
              backgroundSize: '200% 100%',
              animation: 'gradientShift 2s ease-in-out infinite'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h5" sx={{
                mb: 3,
                fontWeight: 700,
                background: 'linear-gradient(45deg, #00d4ff, #4caf50)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textAlign: 'center',
                letterSpacing: '0.5px'
              }}>
                🎯 TRADING CONTROLS & PROJECTIONS
              </Typography>

              {/* Enhanced Trading Action Buttons */}
              <Stack direction="row" spacing={2} sx={{ mb: 3, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={isActive ? <Pause /> : <PlayArrow />}
                  onClick={() => { setConfirmAction(isActive ? 'stop' : 'start'); setConfirmOpen(true); }}
                  sx={{
                    background: isActive
                      ? 'linear-gradient(45deg, #f44336, #d32f2f)'
                      : 'linear-gradient(45deg, #4caf50, #388e3c)',
                    px: 4,
                    py: 1.5,
                    borderRadius: 3,
                    fontWeight: 700,
                    fontSize: '1.1rem',
                    boxShadow: isActive
                      ? '0 4px 20px rgba(244, 67, 54, 0.4)'
                      : '0 4px 20px rgba(76, 175, 80, 0.4)',
                    '&:hover': {
                      background: isActive
                        ? 'linear-gradient(45deg, #d32f2f, #f44336)'
                        : 'linear-gradient(45deg, #388e3c, #4caf50)',
                      transform: 'translateY(-2px) scale(1.05)',
                      boxShadow: isActive
                        ? '0 6px 25px rgba(244, 67, 54, 0.5)'
                        : '0 6px 25px rgba(76, 175, 80, 0.5)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  {isActive ? '⏸️ Stop Trading' : '▶️ Start Trading'}
                </Button>

                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<TrendingUp />}
                  sx={{
                    borderColor: '#00d4ff',
                    color: '#00d4ff',
                    px: 4,
                    py: 1.5,
                    borderRadius: 3,
                    fontWeight: 700,
                    fontSize: '1.1rem',
                    borderWidth: '2px',
                    '&:hover': {
                      borderColor: '#0099cc',
                      backgroundColor: alpha('#00d4ff', 0.15),
                      transform: 'translateY(-2px) scale(1.05)',
                      boxShadow: '0 6px 25px rgba(0, 212, 255, 0.3)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  📈 Manual Order
                </Button>
              </Stack>

              {/* Enhanced Time Period Selection */}
              <Typography variant="h6" sx={{
                mb: 2,
                color: '#00d4ff',
                fontWeight: 600,
                textAlign: 'center'
              }}>
                📊 Investment Outcome Projections
              </Typography>
              <Stack direction="row" spacing={1} sx={{ mb: 3, justifyContent: 'center' }}>
                {(['24h', '48h', '7d', '1m'] as const).map((period) => (
                  <Button
                    key={period}
                    variant={selectedTimePeriod === period ? 'contained' : 'outlined'}
                    size="medium"
                    onClick={() => handleTimePeriodChange(period)}
                    sx={{
                      minWidth: '70px',
                      px: 2,
                      py: 1,
                      borderRadius: 3,
                      fontWeight: 700,
                      fontSize: '0.9rem',
                      backgroundColor: selectedTimePeriod === period ? '#00d4ff' : 'transparent',
                      borderColor: '#00d4ff',
                      borderWidth: '2px',
                      color: selectedTimePeriod === period ? '#000' : '#00d4ff',
                      boxShadow: selectedTimePeriod === period ? '0 4px 15px rgba(0, 212, 255, 0.4)' : 'none',
                      '&:hover': {
                        backgroundColor: selectedTimePeriod === period ? '#0099cc' : alpha('#00d4ff', 0.15),
                        transform: 'translateY(-1px)',
                        boxShadow: selectedTimePeriod === period
                          ? '0 6px 20px rgba(0, 212, 255, 0.5)'
                          : '0 4px 15px rgba(0, 212, 255, 0.3)'
                      },
                      transition: 'all 0.3s ease'
                    }}
                  >
                    {period}
                  </Button>
                ))}
              </Stack>

              {/* Enhanced Investment Projection Display */}
              {projectionData && (
                <Box sx={{
                  p: 3,
                  background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)',
                  border: '2px solid rgba(0, 212, 255, 0.3)',
                  borderRadius: 4,
                  boxShadow: '0 4px 20px rgba(0, 212, 255, 0.2)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    background: 'linear-gradient(90deg, #00d4ff, #4caf50, #00d4ff)',
                    backgroundSize: '200% 100%',
                    animation: 'gradientShift 1.5s ease-in-out infinite'
                  }
                }}>
                  <Typography variant="subtitle2" sx={{ mb: 2, color: '#00d4ff' }}>
                    Projected Outcome ({projectionData.timePeriod}):
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>
                        Projected Value
                      </Typography>
                      <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                        {formatCurrency(projectionData.projectedValue)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>
                        Profit/Loss
                      </Typography>
                      <Typography variant="h6" sx={{
                        color: projectionData.projectedProfit >= 0 ? '#4caf50' : '#f44336',
                        fontWeight: 700
                      }}>
                        {formatCurrencySigned(projectionData.projectedProfit)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>
                        Return %
                      </Typography>
                      <Typography variant="h6" sx={{
                        color: projectionData.projectedReturn >= 0 ? '#4caf50' : '#f44336',
                        fontWeight: 700
                      }}>
                        {projectionData.projectedReturn >= 0 ? '+' : ''}{projectionData.projectedReturn.toFixed(2)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#aaa', display: 'block' }}>
                        Risk Level
                      </Typography>
                      <Typography variant="h6" sx={{
                        color: projectionData.projectedRisk > 20 ? '#f44336' : projectionData.projectedRisk > 10 ? '#ff9800' : '#4caf50',
                        fontWeight: 700
                      }}>
                        {projectionData.projectedRisk.toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Grow in={true} timeout={1000}>
            <Card sx={{
              background: dailyPnL >= 0
                ? `linear-gradient(135deg, ${alpha('#4caf50', 0.15)} 0%, ${alpha('#4caf50', 0.05)} 100%)`
                : `linear-gradient(135deg, ${alpha('#f44336', 0.15)} 0%, ${alpha('#f44336', 0.05)} 100%)`,
              border: dailyPnL >= 0
                ? `2px solid ${alpha('#4caf50', 0.4)}`
                : `2px solid ${alpha('#f44336', 0.4)}`,
              backdropFilter: 'blur(15px)',
              borderRadius: 3,
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden',
              '&:hover': {
                transform: 'translateY(-8px) scale(1.02)',
                boxShadow: dailyPnL >= 0
                  ? '0 12px 30px rgba(76, 175, 80, 0.3)'
                  : '0 12px 30px rgba(244, 67, 54, 0.3)',
                border: dailyPnL >= 0 ? `2px solid #4caf50` : `2px solid #f44336`
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '3px',
                background: dailyPnL >= 0
                  ? 'linear-gradient(90deg, #4caf50, #8bc34a, #4caf50)'
                  : 'linear-gradient(90deg, #f44336, #ff5722, #f44336)',
                backgroundSize: '200% 100%',
                animation: 'shimmer 3s linear infinite'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" sx={{
                    color: dailyPnL >= 0 ? '#4caf50' : '#f44336',
                    fontWeight: 600
                  }}>
                    Daily P&L
                  </Typography>
                  {dailyPnL >= 0 ?
                    <TrendingUp sx={{ color: '#4caf50', fontSize: 28 }} /> :
                    <TrendingDown sx={{ color: '#f44336', fontSize: 28 }} />
                  }
                </Box>
                <Typography variant="h3" sx={{
                  fontWeight: 800,
                  color: dailyPnL >= 0 ? '#4caf50' : '#f44336',
                  mb: 1,
                  textShadow: dailyPnL >= 0
                    ? '0 0 10px rgba(76, 175, 80, 0.5)'
                    : '0 0 10px rgba(244, 67, 54, 0.5)'
                }}>
                  {formatCurrencySigned(dailyPnL)}
                </Typography>
                <Typography variant="caption" sx={{
                  color: '#aaa',
                  fontWeight: 500,
                  letterSpacing: '0.5px'
                }}>
                  Today's Performance
                </Typography>
              </CardContent>
            </Card>
          </Grow>
        </Grid>


      </Grid>



      {/* Advanced Analytics - MOVED TO VERY TOP */}
      {liveAnalytics && (
        <Paper sx={{
          mb: 4,
          p: 3,
          backgroundColor: 'rgba(26, 26, 46, 0.9)',
          border: '2px solid rgba(255, 107, 53, 0.4)',
          borderRadius: 4,
          boxShadow: '0 8px 32px rgba(255, 107, 53, 0.2)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '4px',
            background: 'linear-gradient(90deg, #ff6b35, #00d4ff, #9c27b0, #ff6b35)',
            backgroundSize: '200% 100%',
            animation: 'gradientShift 3s ease-in-out infinite'
          }
        }}>
          <Typography variant="h4" sx={{
            mb: 3,
            fontWeight: 800,
            background: 'linear-gradient(45deg, #ff6b35, #00d4ff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textAlign: 'center',
            letterSpacing: '1px'
          }}>
            📈 ADVANCED ANALYTICS
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={6} md={2}>
              <Tooltip title="Percentage of profitable trades" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: 'rgba(76, 175, 80, 0.12)',
                  border: '1px solid rgba(76, 175, 80, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(76, 175, 80, 0.4)',
                    background: 'rgba(76, 175, 80, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    WIN RATE
                  </Typography>
                  <Box sx={{ mb: 1 }}>
                    <CircularProgressIndicator
                      value={liveAnalytics.winRate}
                      max={100}
                      color={liveAnalytics.winRate >= 60 ? '#4caf50' : liveAnalytics.winRate >= 40 ? '#ff9800' : '#f44336'}
                      label=""
                      size={60}
                    />
                  </Box>
                  <MiniChart
                    data={[65, 68, 72, 69, 71, liveAnalytics.winRate]}
                    color="#4caf50"
                    label="winrate"
                  />
                </Box>
              </Tooltip>
            </Grid>

            <Grid item xs={6} md={2}>
              <Tooltip title="Market volatility indicator" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: 'rgba(233, 30, 99, 0.12)',
                  border: '1px solid rgba(233, 30, 99, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(233, 30, 99, 0.4)',
                    background: 'rgba(233, 30, 99, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    VOLATILITY
                  </Typography>
                  <Typography variant="h4" sx={{
                    color: '#e91e63',
                    fontWeight: 800,
                    fontFamily: 'monospace',
                    fontSize: '1.8rem',
                    mb: 1,
                    textShadow: '0 0 10px rgba(233, 30, 99, 0.5)'
                  }}>
                    {liveAnalytics.volatility.toFixed(2)}%
                  </Typography>
                  <MiniChart
                    data={[15.2, 18.7, 22.1, 19.8, 17.25, liveAnalytics.volatility]}
                    color="#e91e63"
                    label="volatility"
                  />
                </Box>
              </Tooltip>
            </Grid>

            <Grid item xs={6} md={2}>
              <Tooltip title="Portfolio correlation with market" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: 'rgba(156, 39, 176, 0.12)',
                  border: '1px solid rgba(156, 39, 176, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(156, 39, 176, 0.4)',
                    background: 'rgba(156, 39, 176, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    BETA
                  </Typography>
                  <Typography variant="h4" sx={{
                    color: '#9c27b0',
                    fontWeight: 800,
                    fontFamily: 'monospace',
                    fontSize: '1.8rem',
                    mb: 1,
                    textShadow: '0 0 10px rgba(156, 39, 176, 0.5)'
                  }}>
                    {liveAnalytics.beta.toFixed(2)}
                  </Typography>
                  <MiniChart
                    data={[0.85, 0.92, 1.05, 0.98, 0.90, liveAnalytics.beta]}
                    color="#9c27b0"
                    label="beta"
                  />
                </Box>
              </Tooltip>
            </Grid>

            <Grid item xs={6} md={2}>
              <Tooltip title="Excess return over market benchmark" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: liveAnalytics.alpha >= 0 ? 'rgba(76, 175, 80, 0.12)' : 'rgba(244, 67, 54, 0.12)',
                  border: liveAnalytics.alpha >= 0 ? '1px solid rgba(76, 175, 80, 0.4)' : '1px solid rgba(244, 67, 54, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: liveAnalytics.alpha >= 0 ? '0 8px 25px rgba(76, 175, 80, 0.4)' : '0 8px 25px rgba(244, 67, 54, 0.4)',
                    background: liveAnalytics.alpha >= 0 ? 'rgba(76, 175, 80, 0.18)' : 'rgba(244, 67, 54, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    ALPHA
                  </Typography>
                  <Typography variant="h4" sx={{
                    color: liveAnalytics.alpha >= 0 ? '#4caf50' : '#f44336',
                    fontWeight: 800,
                    fontFamily: 'monospace',
                    fontSize: '1.8rem',
                    mb: 1,
                    textShadow: liveAnalytics.alpha >= 0 ? '0 0 10px rgba(76, 175, 80, 0.5)' : '0 0 10px rgba(244, 67, 54, 0.5)'
                  }}>
                    {liveAnalytics.alpha >= 0 ? '+' : ''}{liveAnalytics.alpha.toFixed(2)}
                  </Typography>
                  <MiniChart
                    data={[-0.15, 0.08, 0.22, -0.05, 0.12, liveAnalytics.alpha]}
                    color={liveAnalytics.alpha >= 0 ? '#4caf50' : '#f44336'}
                    label="alpha"
                  />
                </Box>
              </Tooltip>
            </Grid>

            <Grid item xs={6} md={2}>
              <Tooltip title="Average return per trade" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: 'rgba(0, 212, 255, 0.12)',
                  border: '1px solid rgba(0, 212, 255, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0, 212, 255, 0.4)',
                    background: 'rgba(0, 212, 255, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    AVG TRADE
                  </Typography>
                  <Typography variant="h4" sx={{
                    color: '#00d4ff',
                    fontWeight: 800,
                    fontFamily: 'monospace',
                    fontSize: '1.8rem',
                    mb: 1,
                    textShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
                  }}>
                    {liveAnalytics.avgTradeReturn.toFixed(2)}%
                  </Typography>
                  <MiniChart
                    data={[1.2, 1.8, 2.1, 1.5, 1.9, liveAnalytics.avgTradeReturn]}
                    color="#00d4ff"
                    label="avgtrade"
                  />
                </Box>
              </Tooltip>
            </Grid>

            <Grid item xs={6} md={2}>
              <Tooltip title="Risk-adjusted return measure" arrow>
                <Box sx={{
                  textAlign: 'center',
                  p: 2.5,
                  borderRadius: 3,
                  background: 'rgba(255, 152, 0, 0.12)',
                  border: '1px solid rgba(255, 152, 0, 0.4)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(255, 152, 0, 0.4)',
                    background: 'rgba(255, 152, 0, 0.18)'
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                    transition: 'left 0.5s ease',
                  },
                  '&:hover::before': {
                    left: '100%'
                  }
                }}>
                  <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1.5, fontWeight: 600, letterSpacing: '0.5px' }}>
                    SHARPE RATIO
                  </Typography>
                  <Typography variant="h4" sx={{
                    color: '#ff9800',
                    fontWeight: 800,
                    fontFamily: 'monospace',
                    fontSize: '1.8rem',
                    mb: 1,
                    textShadow: '0 0 10px rgba(255, 152, 0, 0.5)'
                  }}>
                    {liveAnalytics.sharpeRatio.toFixed(2)}
                  </Typography>
                  <MiniChart
                    data={[1.05, 1.32, 1.18, 1.45, 1.28, liveAnalytics.sharpeRatio]}
                    color="#ff9800"
                    label="sharpe"
                  />
                </Box>
              </Tooltip>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Trading Mode Selector */}
  {/* If a mode is forced by prop (separate tabs), hide the selector to avoid cross-tab confusion */}
  {!mode && <TradingModeSelector />}


      {/* 48-Hour Trial Showcase */}
  {isDemoView && (
        <Paper sx={{
          mb: 4,
          p: 3,
          background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 53, 0.1) 100%)',
          border: '2px solid rgba(0, 212, 255, 0.3)',
          borderRadius: 3
        }}>
          {/* Real Trading Summary - No Demo Data */}
          {realTradingData && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 2, fontWeight: 700, color: '#00d4ff' }}>
                📊 Real Trading Overview
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6">Paper Trading Account</Typography>
                  <Typography>Balance: ${realTradingData.paperAccount.buying_power.toLocaleString()}</Typography>
                  <Typography>Positions: {realTradingData.paperPositions.length}</Typography>
                  <Typography>Orders: {realTradingData.paperOrders.length}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6">Live Trading Account</Typography>
                  <Typography>Balance: ${realTradingData.liveAccount.buying_power.toLocaleString()}</Typography>
                  <Typography>Positions: {realTradingData.livePositions.length}</Typography>
                  <Typography>Orders: {realTradingData.liveOrders.length}</Typography>
                </Grid>
              </Grid>

              <Typography variant="h6" sx={{ mt: 2 }}>
                Analytics: Today's P&L ${realTradingData.analytics.todaysPnL.toFixed(2)}
              </Typography>
            </Box>
          )}

          <Typography variant="h5" sx={{ mb: 2, fontWeight: 700, color: '#00d4ff' }}>
            🎯 Real Trading Experience
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="body1" sx={{ mb: 3, color: '#aaa' }}>
                Experience the full power of Prometheus trading with $100,000 virtual money.
                Learn, practice, and see why traders choose our platform.
              </Typography>

              {/* Progress Steps */}
              <Stepper activeStep={currentStep} sx={{ mb: 3 }}>
                {investmentSteps.map((label) => (
                  <Step key={label}>
                    <StepLabel sx={{
                      '& .MuiStepLabel-label': { color: '#aaa' },
                      '& .MuiStepLabel-label.Mui-active': { color: '#00d4ff' },
                      '& .MuiStepLabel-label.Mui-completed': { color: '#4caf50' }
                    }}>
                      {label}
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<School />}
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
                    }
                  }}
                  onClick={() => setCurrentStep(Math.min(3, currentStep + 1))}
                >
                  Continue Learning
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Star />}
                  sx={{
                    borderColor: '#ff9800',
                    color: '#ff9800',
                    '&:hover': {
                      borderColor: '#f57c00',
                      backgroundColor: alpha('#ff9800', 0.1)
                    }
                  }}
                >
                  Upgrade to Premium
                </Button>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h3" sx={{
                  fontWeight: 800,
                  color: '#00d4ff',
                  mb: 1
                }}>
                  {realTradingData ? `$${realTradingData.analytics.portfolioValue.toLocaleString()}` : 'Loading...'}
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                  Current Portfolio Value
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={realTradingData ? 100 : 0}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: alpha('#333', 0.3),
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#00d4ff',
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Real-Time Wealth Tracker */}
      {realTradingData && (
        <RealTimeWealthTracker
          portfolioValue={isLiveView ? realTradingData.liveAccount.portfolio_value : realTradingData.paperAccount.portfolio_value}
          isLiveTrading={isLiveView}
          refreshInterval={30000}
        />
      )}

      {/* Live Trading Signals */}
      {tradingSignals.length > 0 && (
        <Paper sx={{
          mb: 4,
          p: 3,
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '2px solid rgba(0, 212, 255, 0.3)',
          borderRadius: 3
        }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, color: '#00d4ff', display: 'flex', alignItems: 'center', gap: 1 }}>
            🤖 Live AI Trading Signals
            <Chip
              label="REAL-TIME"
              size="small"
              sx={{
                backgroundColor: '#4caf50',
                color: 'white',
                animation: 'pulse 2s infinite'
              }}
            />
          </Typography>

          <Grid container spacing={2}>
            {tradingSignals.slice(0, 3).map((signal, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card sx={{
                  backgroundColor: signal.action === 'BUY' ? 'rgba(76, 175, 80, 0.1)' :
                                   signal.action === 'SELL' ? 'rgba(244, 67, 54, 0.1)' :
                                   'rgba(255, 152, 0, 0.1)',
                  border: `1px solid ${signal.action === 'BUY' ? '#4caf50' :
                                      signal.action === 'SELL' ? '#f44336' : '#ff9800'}`,
                  borderRadius: 2
                }}>
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>
                        {signal.symbol}
                      </Typography>
                      <Chip
                        label={signal.action}
                        size="small"
                        sx={{
                          backgroundColor: signal.action === 'BUY' ? '#4caf50' :
                                          signal.action === 'SELL' ? '#f44336' : '#ff9800',
                          color: 'white',
                          fontWeight: 700
                        }}
                      />
                    </Box>
                    <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                      {signal.reason}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption" sx={{ color: '#00d4ff' }}>
                        Confidence: {signal.confidence.toFixed(0)}%
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        Target: ${signal.targetPrice.toFixed(2)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Live Portfolio Positions */}
      {portfolio.length > 0 && (
        <Paper sx={{
          mb: 4,
          p: 3,
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          border: '1px solid rgba(156, 39, 176, 0.3)',
          borderRadius: 3
        }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, color: '#9c27b0' }}>
            📊 Live Portfolio Positions
          </Typography>

          <Grid container spacing={2}>
            {portfolio.slice(0, 4).map((position, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card sx={{
                  backgroundColor: position.unrealizedPnL >= 0 ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
                  border: `1px solid ${position.unrealizedPnL >= 0 ? '#4caf50' : '#f44336'}`,
                  borderRadius: 2
                }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', mb: 1 }}>
                      {position.symbol}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                      {position.quantity} shares @ ${position.avgPrice.toFixed(2)}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                      Current: ${position.currentPrice.toFixed(2)}
                    </Typography>
                    <Typography variant="body1" sx={{
                      fontWeight: 700,
                      color: position.unrealizedPnL >= 0 ? '#4caf50' : '#f44336'
                    }}>
                      {position.unrealizedPnL >= 0 ? '+' : ''}${position.unrealizedPnL.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" sx={{
                      color: position.unrealizedPnL >= 0 ? '#4caf50' : '#f44336'
                    }}>
                      ({position.unrealizedPnLPercent >= 0 ? '+' : ''}{position.unrealizedPnLPercent.toFixed(2)}%)
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Order Management Section */}
      <Box sx={{ mb: 4 }}>
        <OrderManagement 
          mode={effectiveMode} 
          onOrderUpdate={fetchRealTradingData}
        />
      </Box>

      {/* Investment Guidance Section */}
      <Paper sx={{
        mb: 4,
        p: 3,
        backgroundColor: 'rgba(26, 26, 46, 0.8)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 3
      }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, color: '#00d4ff', display: 'flex', alignItems: 'center', gap: 1 }}>
          <Lightbulb /> Why You Should Invest & How to Start
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" sx={{ mb: 2, color: '#4caf50' }}>
              💰 Why Invest with Prometheus?
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText
                  primary="AI-Powered Trading"
                  secondary="Our advanced AI analyzes markets 24/7 to find opportunities"
                  secondaryTypographyProps={{ color: '#aaa' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Risk Management"
                  secondary="Built-in stop-losses and position sizing protect your capital"
                  secondaryTypographyProps={{ color: '#aaa' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle sx={{ color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Proven Results"
                  secondary="Our users average 12-18% annual returns with managed risk"
                  secondaryTypographyProps={{ color: '#aaa' }}
                />
              </ListItem>
            </List>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" sx={{ mb: 2, color: '#ff9800' }}>
              🎯 Recommended Investment Strategies
            </Typography>
            {investmentRecommendations.map((rec, index) => (
              <Card key={index} sx={{
                mb: 2,
                backgroundColor: alpha(rec.color, 0.1),
                border: `1px solid ${alpha(rec.color, 0.3)}`
              }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: rec.color }}>
                      {rec.title}
                    </Typography>
                    <Chip
                      label={rec.riskLevel}
                      size="small"
                      sx={{
                        backgroundColor: rec.color,
                        color: 'white',
                        fontSize: '0.7rem'
                      }}
                    />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                    {rec.description}
                  </Typography>
                  <Typography variant="caption" sx={{ color: rec.color, fontWeight: 600 }}>
                    Expected: {rec.expectedReturn}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      </Paper>




      {/* Status Message */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="body2" sx={{ color: '#aaa', textAlign: 'center' }}>
          {isLiveView
            ? '⚠️ Live trading system ready. All orders will be executed with real money.'
            : isDemoView
            ? '📊 48-hour demo system ready. Practice with virtual money and see real results!'
            : '📈 Paper trading system ready. Practice with virtual money and learn!'
          }
        </Typography>
      </Box>

      {/* Real Portfolio Allocation - No Demo ROI */}
      {realTradingData && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{
            p: 3,
            background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 53, 0.1) 100%)',
            border: '2px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3
          }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, color: '#00d4ff' }}>
              📈 Real Portfolio Allocation
            </Typography>
            {isLiveView ? (
              <>
                <Typography>Live Account: ${realTradingData.liveAccount.buying_power.toLocaleString()}</Typography>
                <Typography>Portfolio Value: ${realTradingData.liveAccount.portfolio_value.toLocaleString()}</Typography>
              </>
            ) : (
              <>
                <Typography>Paper Account: ${realTradingData.paperAccount.buying_power.toLocaleString()}</Typography>
                <Typography>Portfolio Value: ${realTradingData.paperAccount.portfolio_value.toLocaleString()}</Typography>
              </>
            )}
          </Box>
        </Box>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>

      {/* Paper Trading Session Creation Dialog */}
      <Dialog
        open={sessionDialog}
        onClose={() => setSessionDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            border: '1px solid #333'
          }
        }}
      >
        <DialogTitle sx={{ color: '#00d4ff', display: 'flex', alignItems: 'center', gap: 2 }}>
          <PlayArrow />
          Create Paper Trading Session
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ color: '#aaa', mb: 2 }}>
              Choose your paper trading session type and starting capital. Earn achievements and level up as you trade!
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel sx={{ color: '#aaa' }}>Session Type</InputLabel>
                  <Select
                    value={sessionType}
                    onChange={(e) => setSessionType(e.target.value)}
                    sx={{
                      color: '#fff',
                      '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
                      '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' }
                    }}
                  >
                    <MenuItem value="24_hour">⚡ Quick Session (24 hours)</MenuItem>
                    <MenuItem value="48_hour">🚀 Extended Session (48 hours)</MenuItem>
                    <MenuItem value="168_hour">👑 Full Week Challenge (168 hours)</MenuItem>
                    <MenuItem value="custom">⚙️ Custom Duration</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Starting Capital ($)"
                  type="number"
                  value={startingCapital}
                  onChange={(e) => setStartingCapital(e.target.value)}
                  helperText="Choose your virtual starting capital"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: '#fff',
                      '& fieldset': { borderColor: '#333' },
                      '&:hover fieldset': { borderColor: '#00d4ff' },
                      '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                    },
                    '& .MuiInputLabel-root': { color: '#aaa' },
                    '& .MuiFormHelperText-root': { color: '#aaa' }
                  }}
                />
              </Grid>

              {sessionType === 'custom' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Custom Duration (hours)"
                    type="number"
                    value={customHours}
                    onChange={(e) => setCustomHours(e.target.value)}
                    helperText="Enter custom session duration in hours"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        color: '#fff',
                        '& fieldset': { borderColor: '#333' },
                        '&:hover fieldset': { borderColor: '#00d4ff' },
                        '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                      },
                      '& .MuiInputLabel-root': { color: '#aaa' },
                      '& .MuiFormHelperText-root': { color: '#aaa' }
                    }}
                  />
                </Grid>
              )}
            </Grid>
          </Box>

          <Alert
            severity="info"
            sx={{
              backgroundColor: 'rgba(0, 212, 255, 0.1)',
              border: '1px solid #00d4ff',
              '& .MuiAlert-message': { color: '#fff' }
            }}
          >
            <Typography variant="body2">
              <strong>🎮 Gamification Features:</strong> Earn achievements, level up, and compete on leaderboards as you trade.
              Your performance will be tracked and you can unlock new trading features!
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button
            onClick={() => setSessionDialog(false)}
            sx={{ color: '#aaa' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateSession}
            variant="contained"
            disabled={!startingCapital || parseFloat(startingCapital) <= 0 || (sessionType === 'custom' && (!customHours || parseInt(customHours) <= 0))}
            startIcon={<PlayArrow />}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff 30%, #0099cc 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #0099cc 30%, #00d4ff 90%)'
              },
              '&:disabled': {
                background: '#333',
                color: '#666'
              }
            }}
          >
            Create Session
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Memoize the component to prevent unnecessary re-renders
export default memo(TradingDashboard);

