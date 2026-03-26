import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Grid, Chip, alpha, LinearProgress, Button } from '@mui/material';
import {
  TrendingUp,
  Speed,
  Psychology,
  Security,
  CloudDone,
  Timeline,
  Person,
  Dashboard
} from '@mui/icons-material';
import Logo from '../Logo';
import { useSystemHealth } from '../../hooks/useSystemHealth';

/**
 * 🚀 TRADING COMMAND CENTER HEADER
 * Professional dashboard header with live stats and original logo
 */

interface TradingCommandCenterProps {
  user: {
    username: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  onLogout?: () => void;
}

const TradingCommandCenter: React.FC<TradingCommandCenterProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();

  // ✅ FIXED: Use real system health data from backend
  const { metrics: liveStats, isLoading, error } = useSystemHealth(5000);

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'admin': return '#f44336';
      case 'premium': return '#9c27b0';
      default: return '#ff9800';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'admin': return 'SYSTEM ADMIN';
      case 'premium': return 'PREMIUM TRADER';
      default: return 'DEMO TRADER';
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
      {/* Animated Background Grid */}
      <Box sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
          linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '20px 20px',
        animation: 'gridMove 20s linear infinite',
        zIndex: 1
      }} />

      <Box sx={{ position: 'relative', zIndex: 2 }}>
        {/* Top Row - Logo and User Info */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          mb: 3
        }}>
          {/* Logo and Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Logo size="medium" theme="dark" />
            <Box>
              <Typography variant="h4" sx={{
                fontWeight: 800,
                background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                letterSpacing: '1px'
              }}>
                PROMETHEUS
              </Typography>
              <Typography variant="subtitle1" sx={{
                color: '#aaa',
                fontWeight: 600,
                letterSpacing: '1px',
                fontSize: '0.9rem'
              }}>
                WITH NeuroForge™
              </Typography>
            </Box>
          </Box>

          {/* User Info and Time */}
          <Box sx={{ textAlign: 'right' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                {user.username}
              </Typography>
              <Chip
                label={getTierLabel(user.tier)}
                sx={{
                  backgroundColor: alpha(getTierColor(user.tier), 0.2),
                  color: getTierColor(user.tier),
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  border: `1px solid ${getTierColor(user.tier)}`
                }}
              />

              {/* Navigation Buttons */}
              <Button
                variant="outlined"
                size="small"
                startIcon={<Person />}
                onClick={() => navigate('/dashboard')}
                sx={{
                  color: '#00d4ff',
                  borderColor: '#00d4ff',
                  '&:hover': {
                    backgroundColor: alpha('#00d4ff', 0.1),
                    borderColor: '#00d4ff'
                  },
                  fontSize: '0.75rem',
                  px: 2
                }}
              >
                User Dashboard
              </Button>

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
                    fontSize: '0.75rem',
                    px: 2
                  }}
                >
                  Logout
                </Button>
              )}
            </Box>
            <Typography variant="body2" sx={{ color: '#aaa', fontFamily: 'monospace' }}>
              {currentTime.toLocaleTimeString()} EST
            </Typography>
          </Box>
        </Box>

        {/* Live Stats Grid */}
        <Grid container spacing={2}>
          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <CloudDone sx={{ fontSize: 16, color: '#4caf50' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  SYSTEM
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 700, fontFamily: 'monospace' }}>
                {liveStats.systemHealth.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Psychology sx={{ fontSize: 16, color: '#9c27b0' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  AI ACCURACY
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#9c27b0', fontWeight: 700, fontFamily: 'monospace' }}>
                {liveStats.aiAccuracy.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Timeline sx={{ fontSize: 16, color: '#ff9800' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  STRATEGIES
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#ff9800', fontWeight: 700, fontFamily: 'monospace' }}>
                {liveStats.activeStrategies}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <TrendingUp sx={{ fontSize: 16, color: '#00d4ff' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  MARKET
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ 
                color: liveStats.marketStatus === 'OPEN' ? '#4caf50' : '#f44336', 
                fontWeight: 700,
                fontFamily: 'monospace'
              }}>
                {liveStats.marketStatus}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Speed sx={{ fontSize: 16, color: '#e91e63' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  LATENCY
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#e91e63', fontWeight: 700, fontFamily: 'monospace' }}>
                {liveStats.latency.toFixed(1)}ms
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={6} sm={4} md={2}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 1 }}>
                <Security sx={{ fontSize: 16, color: '#00d4ff' }} />
                <Typography variant="caption" sx={{ color: '#aaa', fontWeight: 600 }}>
                  UPTIME
                </Typography>
              </Box>
              <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700, fontFamily: 'monospace' }}>
                {liveStats.uptime.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Status Bar */}
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="caption" sx={{ color: '#aaa' }}>
              SYSTEM STATUS
            </Typography>
            <Typography variant="caption" sx={{ color: '#4caf50', fontFamily: 'monospace' }}>
              ALL SYSTEMS OPERATIONAL
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={liveStats.systemHealth}
            sx={{
              height: 4,
              borderRadius: 2,
              backgroundColor: alpha('#4caf50', 0.2),
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#4caf50',
                borderRadius: 2
              }
            }}
          />
        </Box>
      </Box>

      {/* CSS Animations */}
      <style>{`
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(20px, 20px); }
        }
      `}</style>
    </Box>
  );
};

export default TradingCommandCenter;
