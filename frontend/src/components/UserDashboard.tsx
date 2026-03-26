import React, { useState, useMemo, useCallback, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Button,
  Chip,
  Grid,
  Avatar,
  Paper,
  Stack,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  SmartToy,
  AutoAwesome,
  Psychology,
  Speed,
  Insights,
  TrendingUp,
  Assessment,
  EmojiEvents,
  Star,
  Timeline,
  Person,
  AdminPanelSettings
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import ParticleBackground from './ParticleBackground';
import BrokerAccountManager from './BrokerAccountManager';
import NavigationButton from './common/NavigationButton';
import ErrorBoundary from './common/ErrorBoundary';
import { useUserPortfolio } from '../hooks/useUserPortfolio';
import { useGamification } from '../hooks/useGamification';
import { useRealtimePortfolio } from '../hooks/useRealtimePortfolio';
import Leaderboard from './social/Leaderboard';
import Watchlist from './portfolio/Watchlist';
import TradingAcademy from './education/TradingAcademy';
import GamificationDashboard from './gamification/GamificationDashboard';
import UserDashboardSkeleton from './skeletons/UserDashboardSkeleton';

// User Dashboard Props
interface UserDashboardProps {
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
    avatar?: string;
    tier?: string;
    joinDate?: string;
  };
}

const UserDashboard: React.FC<UserDashboardProps> = ({ user }) => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  // ✅ FIXED: Fetch real portfolio data from API
  const {
    portfolio,
    isLoading: portfolioLoading,
    error: portfolioError
  } = useUserPortfolio(user.id);

  // ✅ FIXED: Fetch real gamification data from API
  const {
    level,
    xp,
    achievements,
    skillRatings,
    badges,
    streak,
    nextLevelXP,
    xpToNextLevel,
    totalAchievements,
    isLoading: gamificationLoading,
    error: gamificationError
  } = useGamification(user.id);

  // ✅ FIXED: Real-time updates via WebSocket
  const { isConnected } = useRealtimePortfolio(user.id);

  // Onboarding tour state
  const [tourRun, setTourRun] = useState(false);

  // Handle loading state - Use skeleton screen for better perceived performance
  if (portfolioLoading || gamificationLoading) {
    return <UserDashboardSkeleton />;
  }

  // Handle error state
  if (portfolioError || gamificationError) {
    return (
      <Box sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        gap: 2,
        p: 3
      }}>
        <Box sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 2
        }}>
          <Typography variant="h3">⚠️</Typography>
        </Box>
        <Typography variant="h5" sx={{ color: '#f44336', fontWeight: 600, textAlign: 'center' }}>
          Failed to load dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 3, textAlign: 'center', maxWidth: 500 }}>
          {portfolioError?.toString() || gamificationError?.toString()}
        </Typography>
        <Button
          variant="contained"
          onClick={() => window.location.reload()}
          sx={{ 
            background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
            transition: 'all 0.2s ease',
            '&:hover': {
              background: 'linear-gradient(45deg, #0099cc, #007aa3)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 12px rgba(0, 212, 255, 0.4)'
            }
          }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  // Safety check for portfolio data
  if (!portfolio) {
    return (
      <Box sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)'
      }}>
        <Typography variant="h6" sx={{ color: '#aaa' }}>
          No portfolio data available
        </Typography>
      </Box>
    );
  }

  // Button handlers - memoized with useCallback
  const handleStartTrading = useCallback(() => {
    navigate('/trading');
    enqueueSnackbar('Opening trading interface...', { variant: 'info' });
  }, [navigate, enqueueSnackbar]);

  const handleAIAssistant = useCallback(() => {
    navigate('/ai-assistant');
    enqueueSnackbar('Launching AI Assistant...', { variant: 'info' });
  }, [navigate, enqueueSnackbar]);

  const handleAnalytics = useCallback(() => {
    navigate('/analytics');
  }, [navigate]);

  // Memoized helper functions
  const getTierColor = useCallback((tier: string) => {
    const colors = {
      rookie: '#9e9e9e',
      trader: '#4caf50',
      expert: '#2196f3',
      master: '#9c27b0',
      legend: '#ff9800',
      oracle: '#f44336'
    };
    return colors[tier as keyof typeof colors] || '#2196f3';
  }, []);

  const getTierIcon = useCallback((tier: string) => {
    switch (tier) {
      case 'oracle': return '🔮';
      case 'legend': return '👑';
      case 'master': return '⭐';
      case 'expert': return '💎';
      case 'trader': return '📈';
      default: return '🌱';
    }
  }, []);

  // Memoized computed values
  const tierColor = useMemo(() => getTierColor(user.tier || 'trader'), [user.tier, getTierColor]);
  const tierIcon = useMemo(() => getTierIcon(user.tier || 'trader'), [user.tier, getTierIcon]);

  return (
    <Box sx={{ 
      position: 'relative',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
      overflow: 'hidden'
    }}>
      {/* Particle Background */}
      <ParticleBackground 
        particleCount={80}
        colors={['#00d4ff', '#ff6b35', '#4caf50', '#9c27b0', '#e91e63', '#ffffff']}
        speed={0.3}
      />

      <Box sx={{ position: 'relative', zIndex: 2, p: 3 }}>
        {/* Onboarding Tour */}
        <OnboardingTour
          steps={getUserDashboardTourSteps()}
          run={tourRun}
          onComplete={() => setTourRun(false)}
          onSkip={() => setTourRun(false)}
        />

        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h4" sx={{ mb: 1, color: '#fff', fontWeight: 600 }}>
                NeuroForge™ Personal Dashboard
              </Typography>
              <Typography variant="h6" sx={{ color: '#00d4ff', fontStyle: 'italic' }}>
                "Your Revolutionary Trading Command Center"
              </Typography>
            </Box>
            {/* Admin Navigation Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              {/* Tour Button */}
              <TourTriggerButton onClick={() => setTourRun(true)} />
              {/* Show cockpit only for admin users */}
              {user?.role === 'admin' && (
                <NavigationButton
                  to="/cockpit"
                  icon={AdminPanelSettings}
                  label="Admin Cockpit"
                  variant="contained"
                  color="secondary"
                  size="large"
                />
              )}
            </Box>
          </Box>

          {/* User Profile Card */}
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: `2px solid ${tierColor}`,
            borderRadius: 3,
            mb: 3,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              boxShadow: `0 8px 32px ${tierColor}40`,
              transform: 'translateY(-4px)',
              borderWidth: '3px'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar 
                  sx={{ 
                    width: 80, 
                    height: 80, 
                    border: `3px solid ${tierColor}`,
                    mr: 3,
                    fontSize: '2rem',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1) rotate(5deg)',
                      boxShadow: `0 8px 24px ${tierColor}60`
                    }
                  }}
                >
                  {tierIcon}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700, mb: 0.5 }}>
                    {user.name}
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1.5 }}>
                    {user.email}
                  </Typography>
                  <Chip 
                    label={`${(user.tier || 'trader').toUpperCase()} TRADER`}
                    sx={{ 
                      bgcolor: tierColor,
                      color: '#fff',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      height: 28,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        transform: 'scale(1.05)',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                      }
                    }}
                  />
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 0.5 }}>
                    Member Since
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 700 }}>
                    {new Date(user.joinDate || '2024-01-15').toLocaleDateString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Portfolio Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <Card 
              data-tour="portfolio-card"
              sx={{ 
                background: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: 3,
                height: '100%',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 8px 32px rgba(0, 212, 255, 0.2)',
                  borderColor: 'rgba(0, 212, 255, 0.5)',
                  transform: 'translateY(-4px)'
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700 }}>
                    💰 Portfolio Performance
                  </Typography>
                  {isConnected && (
                    <Chip 
                      label="Live" 
                      size="small"
                      sx={{
                        bgcolor: '#4caf50',
                        color: '#fff',
                        fontWeight: 600,
                        animation: 'pulse 2s ease-in-out infinite',
                        '@keyframes pulse': {
                          '0%, 100%': { opacity: 1 },
                          '50%': { opacity: 0.7 }
                        }
                      }}
                    />
                  )}
                </Box>
                
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 212, 255, 0.05)',
                        transform: 'translateY(-2px)'
                      }
                    }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 1, fontWeight: 500 }}>
                        Total Value
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 700, fontFamily: 'monospace' }}>
                        ${portfolio.totalValue.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(76, 175, 80, 0.05)',
                        transform: 'translateY(-2px)'
                      }
                    }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 1, fontWeight: 500 }}>
                        Total Return
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 700, fontFamily: 'monospace' }}>
                        +${portfolio.totalReturn.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(76, 175, 80, 0.05)',
                        transform: 'translateY(-2px)'
                      }
                    }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 1, fontWeight: 500 }}>
                        Return %
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 700 }}>
                        +{portfolio.returnPercentage.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        transform: 'translateY(-2px)'
                      }
                    }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 1, fontWeight: 500 }}>
                        Invested
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700, fontFamily: 'monospace' }}>
                        ${portfolio.totalInvested.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                      Performance Progress
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#4caf50', fontWeight: 600 }}>
                      {Math.min(100, portfolio.returnPercentage * 2).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.min(100, portfolio.returnPercentage * 2)}
                    sx={{ 
                      height: 12,
                      borderRadius: 6,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #4caf50, #8bc34a)',
                        borderRadius: 6,
                        transition: 'width 0.6s ease'
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card 
              data-tour="quick-actions"
              sx={{ 
                background: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(255, 107, 53, 0.3)',
                borderRadius: 3,
                height: '100%',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 8px 32px rgba(255, 107, 53, 0.2)',
                  borderColor: 'rgba(255, 107, 53, 0.5)',
                  transform: 'translateY(-4px)'
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h5" sx={{ color: '#fff', mb: 3, fontWeight: 700 }}>
                  🎯 Quick Actions
                </Typography>
                
                <Stack spacing={2}>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<TrendingUp />}
                    onClick={handleStartTrading}
                    sx={{
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      color: '#000',
                      fontWeight: 700,
                      py: 1.5,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #0099cc, #007aa3)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 12px rgba(0, 212, 255, 0.4)'
                      }
                    }}
                  >
                    Start Trading
                  </Button>

                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<SmartToy />}
                    onClick={handleAIAssistant}
                    sx={{
                      borderColor: '#ff6b35',
                      color: '#ff6b35',
                      borderWidth: 2,
                      py: 1.5,
                      fontWeight: 600,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: 'rgba(255, 107, 53, 0.1)',
                        borderColor: '#ff6b35',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 8px rgba(255, 107, 53, 0.3)'
                      }
                    }}
                  >
                    AI Assistant
                  </Button>

                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<Assessment />}
                    onClick={handleAnalytics}
                    sx={{
                      borderColor: '#4caf50',
                      color: '#4caf50',
                      borderWidth: 2,
                      py: 1.5,
                      fontWeight: 600,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: 'rgba(76, 175, 80, 0.1)',
                        borderColor: '#4caf50',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 8px rgba(76, 175, 80, 0.3)'
                      }
                    }}
                  >
                    Analytics
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Gamification & Progress Section */}
        <Box sx={{ mb: 4 }} data-tour="gamification">
          <Typography variant="h5" sx={{ mb: 1, color: '#fff', fontWeight: 700 }}>
            🎮 Trading Progress & Achievements
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 3 }}>
            Track your trading journey and unlock achievements
          </Typography>
          
          {/* Enhanced Gamification Dashboard */}
          <GamificationDashboard userId={user.id} />
        </Box>

        {/* Legacy Gamification Cards (Optional - can be removed if using full dashboard) */}
        {false && (
        <Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Level & Experience */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #00d4ff',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                boxShadow: '0 8px 32px rgba(0, 212, 255, 0.3)',
                borderColor: '#00d4ff',
                transform: 'translateY(-4px)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box sx={{
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1) rotate(5deg)',
                      backgroundColor: 'rgba(0, 212, 255, 0.2)'
                    }
                  }}>
                    <EmojiEvents sx={{ color: '#00d4ff', fontSize: 32 }} />
                  </Box>
                  <Box>
                    <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 700, mb: 0.5 }}>
                      Level {level}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                      {xp.toLocaleString()} XP
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                      Progress to Level {level + 1}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 700 }}>
                      {nextLevelXP > 0 ? Math.round((xpToNextLevel / nextLevelXP) * 100) : 0}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={nextLevelXP > 0 ? (xpToNextLevel / nextLevelXP) * 100 : 0}
                    sx={{
                      height: 12,
                      borderRadius: 6,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #00d4ff, #0099cc)',
                        borderRadius: 6,
                        transition: 'width 0.6s ease',
                        boxShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
                      }
                    }}
                  />
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: 'rgba(76, 175, 80, 0.1)',
                      border: '1px solid rgba(76, 175, 80, 0.2)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(76, 175, 80, 0.15)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 12px rgba(76, 175, 80, 0.2)'
                      }
                    }}>
                      <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 700, mb: 0.5 }}>
                        {totalAchievements}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                        Achievements
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ 
                      textAlign: 'center',
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 152, 0, 0.1)',
                      border: '1px solid rgba(255, 152, 0, 0.2)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 152, 0, 0.15)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 4px 12px rgba(255, 152, 0, 0.2)'
                      }
                    }}>
                      <Typography variant="h5" sx={{ color: '#ff9800', fontWeight: 700, mb: 0.5 }}>
                        {streak}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontWeight: 500 }}>
                        Day Streak 🔥
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Skill Ratings */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #4caf50',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                boxShadow: '0 8px 32px rgba(76, 175, 80, 0.3)',
                borderColor: '#4caf50',
                transform: 'translateY(-4px)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box sx={{
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1) rotate(-5deg)',
                      backgroundColor: 'rgba(76, 175, 80, 0.2)'
                    }
                  }}>
                    <Assessment sx={{ color: '#4caf50', fontSize: 32 }} />
                  </Box>
                  <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 700 }}>
                    Skill Ratings
                  </Typography>
                </Box>

                {Object.entries(skillRatings).map(([skill, rating]) => (
                  <Box 
                    key={skill} 
                    sx={{ 
                      mb: 2.5,
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        transform: 'translateX(4px)'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                      <Typography variant="body2" sx={{ color: '#fff', textTransform: 'capitalize', fontWeight: 600 }}>
                        {skill.replace('_', ' ')}
                      </Typography>
                      <Typography variant="body2" sx={{ 
                        color: rating >= 80 ? '#4caf50' : rating >= 60 ? '#ff9800' : '#f44336',
                        fontWeight: 700,
                        fontFamily: 'monospace'
                      }}>
                        {rating.toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={rating}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        transition: 'all 0.3s ease',
                        '& .MuiLinearProgress-bar': {
                          background: `linear-gradient(90deg, ${rating >= 80 ? '#4caf50' : rating >= 60 ? '#ff9800' : '#f44336'}, ${rating >= 80 ? '#66bb6a' : rating >= 60 ? '#ffb74d' : '#ef5350'})`,
                          borderRadius: 4,
                          transition: 'width 0.6s ease',
                          boxShadow: `0 0 8px ${rating >= 80 ? 'rgba(76, 175, 80, 0.5)' : rating >= 60 ? 'rgba(255, 152, 0, 0.5)' : 'rgba(244, 67, 54, 0.5)'}`
                        }
                      }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Achievements */}
          <Grid item xs={12}>
            <Card sx={{
              background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
              border: '1px solid #ff9800',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                boxShadow: '0 8px 32px rgba(255, 152, 0, 0.3)',
                borderColor: '#ff9800',
                transform: 'translateY(-4px)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Box sx={{
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1) rotate(5deg)',
                      backgroundColor: 'rgba(255, 152, 0, 0.2)'
                    }
                  }}>
                    <Star sx={{ color: '#ff9800', fontSize: 32 }} />
                  </Box>
                  <Typography variant="h5" sx={{ color: '#ff9800', fontWeight: 700 }}>
                    Recent Achievements
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  {achievements.length > 0 ? (
                    achievements.map((achievement, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Card sx={{
                          background: 'rgba(255, 152, 0, 0.1)',
                          border: '1px solid rgba(255, 152, 0, 0.3)',
                          borderRadius: 2,
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            background: 'rgba(255, 152, 0, 0.15)',
                            borderColor: 'rgba(255, 152, 0, 0.5)',
                            transform: 'translateY(-4px) scale(1.02)',
                            boxShadow: '0 8px 24px rgba(255, 152, 0, 0.2)'
                          }
                        }}>
                          <CardContent sx={{ p: 2.5 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                              <Typography variant="h4" sx={{ mr: 1.5, transition: 'transform 0.3s ease' }}>
                                {achievement.icon}
                              </Typography>
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="subtitle2" sx={{ color: '#fff', fontWeight: 700, mb: 0.5 }}>
                                  {achievement.name}
                                </Typography>
                                <Chip 
                                  label={`+${achievement.points} XP`}
                                  size="small"
                                  sx={{
                                    bgcolor: 'rgba(255, 152, 0, 0.2)',
                                    color: '#ff9800',
                                    fontWeight: 700,
                                    height: 20,
                                    fontSize: '0.7rem'
                                  }}
                                />
                              </Box>
                            </Box>
                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.85rem', lineHeight: 1.5 }}>
                              {achievement.description}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))
                  ) : (
                    <Grid item xs={12}>
                      <Box sx={{ 
                        textAlign: 'center', 
                        py: 6,
                        borderRadius: 2,
                        backgroundColor: 'rgba(255, 152, 0, 0.05)'
                      }}>
                        <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1 }}>
                          No achievements yet
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.3)' }}>
                          Start trading to unlock your first achievement!
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Revolutionary Features Showcase */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 1, color: '#fff', fontWeight: 700 }}>
            🚀 Revolutionary Features Status
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 3 }}>
            Track your progress across all platform features
          </Typography>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'rgba(0, 212, 255, 0.6)',
                transform: 'translateY(-6px)',
                boxShadow: '0 12px 40px rgba(0, 212, 255, 0.25)',
                background: 'rgba(26, 26, 26, 0.98)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                  <Box sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <SmartToy sx={{ color: '#00d4ff', fontSize: 28 }} />
                  </Box>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                    AI Personas
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 2.5 }}>
                  Unlocked trading personalities
                </Typography>
                <Typography variant="h3" sx={{ color: '#00d4ff', fontWeight: 700, mb: 2, fontFamily: 'monospace' }}>
                  {badges.length}/7
                </Typography>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                      Progress
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      {Math.round((badges.length / 7) * 100)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(badges.length / 7) * 100}
                    sx={{ 
                      height: 10,
                      borderRadius: 5,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #00d4ff, #0099cc)',
                        borderRadius: 5,
                        transition: 'width 0.6s ease',
                        boxShadow: '0 0 10px rgba(0, 212, 255, 0.5)'
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 107, 53, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'rgba(255, 107, 53, 0.6)',
                transform: 'translateY(-6px)',
                boxShadow: '0 12px 40px rgba(255, 107, 53, 0.25)',
                background: 'rgba(26, 26, 26, 0.98)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                  <Box sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <EmojiEvents sx={{ color: '#ff6b35', fontSize: 28 }} />
                  </Box>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                    Gamification
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 2.5 }}>
                  Current level & achievements
                </Typography>
                <Typography variant="h3" sx={{ color: '#ff6b35', fontWeight: 700, mb: 2, fontFamily: 'monospace' }}>
                  Level {level}
                </Typography>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                      Progress to Max
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#ff6b35', fontWeight: 600 }}>
                      {Math.round((level / 50) * 100)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(level / 50) * 100}
                    sx={{ 
                      height: 10,
                      borderRadius: 5,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #ff6b35, #ff8c42)',
                        borderRadius: 5,
                        transition: 'width 0.6s ease',
                        boxShadow: '0 0 10px rgba(255, 107, 53, 0.5)'
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: 3,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'rgba(76, 175, 80, 0.6)',
                transform: 'translateY(-6px)',
                boxShadow: '0 12px 40px rgba(76, 175, 80, 0.25)',
                background: 'rgba(26, 26, 26, 0.98)'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                  <Box sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <Psychology sx={{ color: '#4caf50', fontSize: 28 }} />
                  </Box>
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700 }}>
                    Oracle Accuracy
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 2.5 }}>
                  Market prediction success rate
                </Typography>
                <Typography variant="h3" sx={{ color: '#4caf50', fontWeight: 700, mb: 2, fontFamily: 'monospace' }}>
                  {skillRatings.market_analysis.toFixed(1)}%
                </Typography>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                      Accuracy
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#4caf50', fontWeight: 600 }}>
                      {skillRatings.market_analysis >= 80 ? 'Excellent' : skillRatings.market_analysis >= 60 ? 'Good' : 'Improving'}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={skillRatings.market_analysis}
                    sx={{ 
                      height: 10,
                      borderRadius: 5,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.3s ease',
                      '& .MuiLinearProgress-bar': {
                        background: `linear-gradient(90deg, ${skillRatings.market_analysis >= 80 ? '#4caf50' : skillRatings.market_analysis >= 60 ? '#ff9800' : '#f44336'}, ${skillRatings.market_analysis >= 80 ? '#66bb6a' : skillRatings.market_analysis >= 60 ? '#ffb74d' : '#ef5350'})`,
                        borderRadius: 5,
                        transition: 'width 0.6s ease',
                        boxShadow: `0 0 10px ${skillRatings.market_analysis >= 80 ? 'rgba(76, 175, 80, 0.5)' : skillRatings.market_analysis >= 60 ? 'rgba(255, 152, 0, 0.5)' : 'rgba(244, 67, 54, 0.5)'}`
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Social & Educational Features */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Leaderboard */}
          <Grid item xs={12} md={6}>
            <Leaderboard
              currentUserId={user.id}
              onFollowUser={(userId) => {
                enqueueSnackbar(`Following user ${userId}`, { variant: 'info' });
              }}
              onViewProfile={(userId) => {
                enqueueSnackbar(`Viewing profile for user ${userId}`, { variant: 'info' });
              }}
            />
          </Grid>

          {/* Watchlist */}
          <Grid item xs={12} md={6}>
            <Watchlist
              userId={user.id}
              onAddToPortfolio={(symbol) => {
                enqueueSnackbar(`Adding ${symbol} to portfolio`, { variant: 'info' });
              }}
              onSetPriceAlert={(symbol, alert) => {
                enqueueSnackbar(`Price alert set for ${symbol}`, { variant: 'success' });
              }}
            />
          </Grid>
        </Grid>

        {/* Trading Academy */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <TradingAcademy
              userId={user.id}
              onStartLesson={(lessonId) => {
                enqueueSnackbar(`Starting lesson ${lessonId}`, { variant: 'info' });
              }}
              onEnrollCourse={(courseId) => {
                enqueueSnackbar(`Enrolled in course ${courseId}`, { variant: 'success' });
              }}
            />
          </Grid>
        </Grid>

        {/* Broker Account Manager */}
        <Card sx={{ 
          background: 'rgba(26, 26, 26, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 3,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 32px rgba(255, 255, 255, 0.1)',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            transform: 'translateY(-2px)'
          }
        }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h5" sx={{ color: '#fff', mb: 3, fontWeight: 700 }}>
              🏦 Broker Account Management
            </Typography>
            <BrokerAccountManager />
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

// Memoize the component to prevent unnecessary re-renders
export default memo(UserDashboard);
