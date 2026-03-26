import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Chip, alpha, LinearProgress, Button } from '@mui/material';
import { 
  Analytics, 
  TrendingUp, 
  TrendingDown,
  ShowChart,
  Speed,
  Psychology
} from '@mui/icons-material';
import Logo from '../Logo';

/**
 * 📊 ANALYTICS PRO HEADER
 * Data-focused header with advanced metrics and charts
 */

interface AnalyticsProHeaderProps {
  user: {
    username: string;
    email: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  onLogout?: () => void;
}

const AnalyticsProHeader: React.FC<AnalyticsProHeaderProps> = ({ user, onLogout }) => {
  const [metrics, setMetrics] = useState({
    portfolioGrowth: 12.5,
    winRate: 68.3,
    sharpeRatio: 1.42,
    maxDrawdown: -5.2,
    totalTrades: 247,
    avgReturn: 2.8,
    volatility: 15.6,
    beta: 0.85
  });

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      // Simulate live data updates
      setMetrics(prev => ({
        ...prev,
        portfolioGrowth: prev.portfolioGrowth + (Math.random() - 0.5) * 0.1,
        winRate: Math.max(0, Math.min(100, prev.winRate + (Math.random() - 0.5) * 0.2)),
        avgReturn: prev.avgReturn + (Math.random() - 0.5) * 0.05
      }));
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'admin': return '#f44336';
      case 'premium': return '#9c27b0';
      default: return '#ff9800';
    }
  };

  return (
    <Box sx={{
      background: 'linear-gradient(135deg, rgba(10, 10, 10, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%)',
      border: '1px solid rgba(0, 212, 255, 0.2)',
      borderRadius: 3,
      p: 3,
      mb: 4,
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Data Grid Background */}
      <Box sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          linear-gradient(rgba(0, 212, 255, 0.02) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '30px 30px',
        animation: 'dataFlow 15s linear infinite',
        zIndex: 1
      }} />

      <Box sx={{ position: 'relative', zIndex: 2 }}>
        {/* Header Row */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: 3
        }}>
          {/* Logo and Analytics Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Logo size="medium" theme="dark" />
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Analytics sx={{ color: '#00d4ff', fontSize: 28 }} />
                <Typography variant="h4" sx={{
                  fontWeight: 800,
                  background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  letterSpacing: '1px'
                }}>
                  PROMETHEUS
                </Typography>
              </Box>
              <Typography variant="subtitle1" sx={{
                color: '#aaa',
                fontWeight: 600,
                letterSpacing: '1px',
                fontSize: '0.9rem'
              }}>
                ANALYTICS PRO • {currentTime.toLocaleTimeString()}
              </Typography>
            </Box>
          </Box>

          {/* User Info */}
          <Box sx={{ textAlign: 'right' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'flex-end', mb: 0.5 }}>
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                {user.username}
              </Typography>
              {onLogout && (
                <Button
                  variant="outlined"
                  size="small"
                  onClick={onLogout}
                  sx={{
                    color: '#ff6b35',
                    borderColor: '#ff6b35',
                    '&:hover': {
                      backgroundColor: alpha('#ff6b35', 0.1),
                      borderColor: '#ff6b35'
                    },
                    fontSize: '0.7rem',
                    px: 1.5,
                    py: 0.5,
                    minWidth: 'auto'
                  }}
                >
                  Logout
                </Button>
              )}
            </Box>
            <Chip
              label={user.tier.toUpperCase()}
              sx={{
                backgroundColor: alpha(getTierColor(user.tier), 0.2),
                color: getTierColor(user.tier),
                fontWeight: 700,
                fontSize: '0.75rem',
                border: `1px solid ${getTierColor(user.tier)}`
              }}
            />
          </Box>
        </Box>

        {/* Advanced Metrics Grid */}
        <Grid container spacing={2}>
          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                {metrics.portfolioGrowth >= 0 ? (
                  <TrendingUp sx={{ fontSize: 14, color: '#4caf50' }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 14, color: '#f44336' }} />
                )}
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  GROWTH
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ 
                color: metrics.portfolioGrowth >= 0 ? '#4caf50' : '#f44336', 
                fontWeight: 700, 
                fontFamily: 'monospace',
                fontSize: '0.9rem'
              }}>
                {metrics.portfolioGrowth >= 0 ? '+' : ''}{metrics.portfolioGrowth.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <ShowChart sx={{ fontSize: 14, color: '#9c27b0' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  WIN RATE
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#9c27b0', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.winRate.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Speed sx={{ fontSize: 14, color: '#ff9800' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  SHARPE
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#ff9800', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.sharpeRatio.toFixed(2)}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <TrendingDown sx={{ fontSize: 14, color: '#f44336' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  DRAWDOWN
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#f44336', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.maxDrawdown.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Psychology sx={{ fontSize: 14, color: '#e91e63' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  TRADES
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#e91e63', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.totalTrades}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <TrendingUp sx={{ fontSize: 14, color: '#00d4ff' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  AVG RET
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.avgReturn.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <ShowChart sx={{ fontSize: 14, color: '#ff6b35' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  VOLATILITY
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#ff6b35', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.volatility.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={3} md={1.5}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Speed sx={{ fontSize: 14, color: '#4caf50' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600, fontSize: '0.7rem' }}>
                  BETA
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.9rem' }}>
                {metrics.beta.toFixed(2)}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Performance Bar */}
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="caption" sx={{ color: '#aaa' }}>
              PORTFOLIO PERFORMANCE
            </Typography>
            <Typography variant="caption" sx={{ 
              color: metrics.portfolioGrowth >= 0 ? '#4caf50' : '#f44336', 
              fontFamily: 'monospace',
              fontWeight: 700
            }}>
              {metrics.portfolioGrowth >= 0 ? '+' : ''}{metrics.portfolioGrowth.toFixed(2)}% YTD
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(100, Math.max(0, (metrics.portfolioGrowth + 20) * 2.5))}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: alpha('#333', 0.3),
              '& .MuiLinearProgress-bar': {
                backgroundColor: metrics.portfolioGrowth >= 0 ? '#4caf50' : '#f44336',
                borderRadius: 3
              }
            }}
          />
        </Box>
      </Box>

      {/* CSS Animations */}
      <style>{`
        @keyframes dataFlow {
          0% { transform: translate(0, 0); }
          100% { transform: translate(30px, 30px); }
        }
      `}</style>
    </Box>
  );
};

export default AnalyticsProHeader;
