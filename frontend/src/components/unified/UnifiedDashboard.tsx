import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  alpha,
  Paper
} from '@mui/material';
import TradingCommandCenter from './TradingCommandCenter';
import HolographicHeader from './HolographicHeader';
import MinimalHeader from './MinimalHeader';
import AnalyticsProHeader from './AnalyticsProHeader';
import PrometheusLogo from './PrometheusLogo';
import {
  TrendingUp,
  AccountBalance,
  Psychology,
  Settings,
  Person,
  ExitToApp,
  Dashboard as DashboardIcon
} from '@mui/icons-material';

/**
 * 🎯 UNIFIED DASHBOARD - CLEAN & SEAMLESS
 * 
 * FEATURES:
 * - Single, unified interface for all user types
 * - Tier-based feature visibility
 * - Clean, modern design
 * - No duplicated elements
 * - Responsive layout
 * - Intuitive navigation
 */

interface UnifiedDashboardProps {
  user: {
    id: string;
    username: string;
    email: string;
    role: string;
    tier: 'demo' | 'premium' | 'admin';
    avatar?: string;
  };
  onLogout: () => void;
  selectedHeader?: string;
  onHeaderChange?: (headerId: string) => void;
}

interface DashboardCard {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  value: string | number;
  change?: number;
  color: string;
  tier: string[];
  action?: () => void;
}

const UnifiedDashboard: React.FC<UnifiedDashboardProps> = ({
  user,
  onLogout,
  selectedHeader = 'command-center',
  onHeaderChange
}) => {
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);
  const [dashboardData] = useState({
    portfolioValue: 125430.50,
    dailyPnL: 2340.75,
    totalTrades: 47,
    winRate: 68.5,
    aiAccuracy: 94.2,
    systemHealth: 'Excellent'
  });

  // Define dashboard cards based on user tier
  const dashboardCards: DashboardCard[] = [
    {
      id: 'portfolio',
      title: 'Portfolio Value',
      description: 'Total account value',
      icon: AccountBalance,
      value: `$${dashboardData.portfolioValue.toLocaleString()}`,
      change: 3.2,
      color: '#00d4ff',
      tier: ['demo', 'premium', 'admin']
    },
    {
      id: 'pnl',
      title: 'Daily P&L',
      description: 'Today\'s profit/loss',
      icon: TrendingUp,
      value: `$${dashboardData.dailyPnL.toLocaleString()}`,
      change: 12.5,
      color: '#4caf50',
      tier: ['demo', 'premium', 'admin']
    },
    {
      id: 'trades',
      title: 'Total Trades',
      description: 'Executed today',
      icon: DashboardIcon,
      value: dashboardData.totalTrades,
      color: '#ff9800',
      tier: ['demo', 'premium', 'admin']
    },
    {
      id: 'winrate',
      title: 'Win Rate',
      description: 'Success percentage',
      icon: TrendingUp,
      value: `${dashboardData.winRate}%`,
      color: '#9c27b0',
      tier: ['demo', 'premium', 'admin']
    },
    {
      id: 'ai',
      title: 'AI Accuracy',
      description: 'AI prediction accuracy',
      icon: Psychology,
      value: `${dashboardData.aiAccuracy}%`,
      color: '#e91e63',
      tier: ['premium', 'admin']
    },
    {
      id: 'system',
      title: 'System Health',
      description: 'Overall system status',
      icon: Settings,
      value: dashboardData.systemHealth,
      color: '#4caf50',
      tier: ['admin']
    }
  ];

  // Filter cards based on user tier
  const visibleCards = dashboardCards.filter(card =>
    card.tier.includes(user.tier)
  );

  // Render selected header
  const renderHeader = () => {
    switch (selectedHeader) {
      case 'analytics-pro':
        return <AnalyticsProHeader user={user} onLogout={onLogout} />;
      case 'holographic':
        return <HolographicHeader user={user} onLogout={onLogout} />;
      case 'minimal':
        return <MinimalHeader user={user} onLogout={onLogout} />;
      case 'command-center':
      default:
        return <TradingCommandCenter user={user} onLogout={onLogout} />;
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'demo': return '#ff9800';
      case 'premium': return '#9c27b0';
      case 'admin': return '#f44336';
      default: return '#757575';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'demo': return 'Demo Trader';
      case 'premium': return 'Premium Trader';
      case 'admin': return 'System Admin';
      default: return 'User';
    }
  };

  return (
    <Box sx={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${alpha('#0a0a0a', 0.95)} 0%, ${alpha('#1a1a2e', 0.95)} 100%)`,
      color: 'white'
    }}>
      {/* Dynamic Header */}
      {renderHeader()}

      {/* Main Dashboard Content */}


      {/* Main Dashboard Content */}
      <Box sx={{ p: 3 }}>
        {/* Enhanced Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" sx={{
            mb: 2,
            fontWeight: 800,
            background: 'linear-gradient(45deg, #ffffff, #00d4ff)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Welcome back, {user.username}! 🚀
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h6" sx={{ color: '#aaa' }}>
              {user.tier === 'demo' && '⏰ Your 48-hour demo is active. Upgrade to Premium for live trading.'}
              {user.tier === 'premium' && '🎯 Premium features unlocked. Ready for live trading.'}
              {user.tier === 'admin' && '👑 Full system access enabled. All features available.'}
            </Typography>
          </Box>

          {/* Live Status Indicators */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              label="🟢 System Online"
              sx={{
                backgroundColor: alpha('#4caf50', 0.2),
                color: '#4caf50',
                fontWeight: 600,
                animation: 'pulse 2s infinite'
              }}
            />
            <Chip
              label="🤖 AI Active"
              sx={{
                backgroundColor: alpha('#9c27b0', 0.2),
                color: '#9c27b0',
                fontWeight: 600
              }}
            />
            {user.tier !== 'demo' && (
              <Chip
                label="💰 Live Trading Ready"
                sx={{
                  backgroundColor: alpha('#ff9800', 0.2),
                  color: '#ff9800',
                  fontWeight: 600
                }}
              />
            )}
          </Box>
        </Box>

        {/* Dashboard Cards Grid */}
        <Grid container spacing={3}>
          {visibleCards.map((card) => (
            <Grid item xs={12} sm={6} md={4} key={card.id}>
              <Card sx={{
                background: `linear-gradient(135deg, ${alpha(card.color, 0.1)} 0%, ${alpha(card.color, 0.05)} 100%)`,
                border: `1px solid ${alpha(card.color, 0.3)}`,
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s ease',
                cursor: card.action ? 'pointer' : 'default',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 32px ${alpha(card.color, 0.3)}`
                }
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{
                      p: 1,
                      borderRadius: 2,
                      backgroundColor: alpha(card.color, 0.2),
                      mr: 2
                    }}>
                      <card.icon sx={{ color: card.color, fontSize: 24 }} />
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {card.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        {card.description}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Typography variant="h4" sx={{ 
                    color: card.color, 
                    fontWeight: 700,
                    mb: 1
                  }}>
                    {card.value}
                  </Typography>
                  
                  {card.change && (
                    <Chip
                      label={`${card.change > 0 ? '+' : ''}${card.change}%`}
                      size="small"
                      sx={{
                        backgroundColor: card.change > 0 ? alpha('#4caf50', 0.2) : alpha('#f44336', 0.2),
                        color: card.change > 0 ? '#4caf50' : '#f44336'
                      }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Enhanced Quick Actions */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{
            mb: 3,
            fontWeight: 700,
            background: 'linear-gradient(45deg, #00d4ff, #9c27b0)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            ⚡ Quick Actions
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={<TrendingUp />}
                sx={{
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  py: 2,
                  borderRadius: 3,
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  boxShadow: '0 8px 25px rgba(0, 212, 255, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #0099cc, #00d4ff)',
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 35px rgba(0, 212, 255, 0.4)'
                  },
                  transition: 'all 0.3s ease'
                }}
              >
                Start Trading
              </Button>
            </Grid>

            {user.tier !== 'demo' && (
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  fullWidth
                  size="large"
                  startIcon={<AccountBalance />}
                  sx={{
                    borderColor: '#4caf50',
                    color: '#4caf50',
                    py: 2,
                    borderRadius: 3,
                    fontWeight: 700,
                    fontSize: '1.1rem',
                    borderWidth: 2,
                    '&:hover': {
                      borderColor: '#388e3c',
                      backgroundColor: alpha('#4caf50', 0.1),
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 35px rgba(76, 175, 80, 0.3)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  Live Trading
                </Button>
              </Grid>
            )}

            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                size="large"
                startIcon={<Psychology />}
                sx={{
                  borderColor: '#9c27b0',
                  color: '#9c27b0',
                  py: 2,
                  borderRadius: 3,
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  borderWidth: 2,
                  '&:hover': {
                    borderColor: '#7b1fa2',
                    backgroundColor: alpha('#9c27b0', 0.1),
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 35px rgba(156, 39, 176, 0.3)'
                  },
                  transition: 'all 0.3s ease'
                }}
              >
                AI Analytics
              </Button>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                size="large"
                startIcon={<Settings />}
                sx={{
                  borderColor: '#ff9800',
                  color: '#ff9800',
                  py: 2,
                  borderRadius: 3,
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  borderWidth: 2,
                  '&:hover': {
                    borderColor: '#f57c00',
                    backgroundColor: alpha('#ff9800', 0.1),
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 35px rgba(255, 152, 0, 0.3)'
                  },
                  transition: 'all 0.3s ease'
                }}
              >
                Settings
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Additional CSS for animations */}
        <style>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
          }
        `}</style>
      </Box>
    </Box>
  );
};

export default UnifiedDashboard;
