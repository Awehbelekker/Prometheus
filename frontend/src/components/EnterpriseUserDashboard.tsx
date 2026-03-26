import React, { useState } from 'react';
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
  Divider
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
  Person
} from '@mui/icons-material';
import ParticleBackground from './ParticleBackground';
import BrokerAccountManager from './BrokerAccountManager';

// Enterprise User Dashboard Props
interface EnterpriseUserDashboardProps {
  user?: {
    id: string;
    name: string;
    email: string;
    role: string;
    avatar?: string;
    tier?: string;
    joinDate?: string;
  };
  portfolio?: {
    totalValue: number;
    totalInvested: number;
    totalReturn: number;
    returnPercentage: number;
    currency: string;
  };
  revolutionaryFeatures?: {
    aiPersonasUnlocked: number;
    gamificationLevel: number;
    socialFollowers: number;
    tradingStreak: number;
    oracleAccuracy: number;
  };
}

const EnterpriseUserDashboard: React.FC<EnterpriseUserDashboardProps> = ({
  user = {
    id: '1',
    name: 'Professional Trader',
    email: 'trader@neuroforge.com',
    role: 'trader',
    tier: 'expert',
    joinDate: '2024-01-15'
  },
  portfolio = {
    totalValue: 125000,
    totalInvested: 100000,
    totalReturn: 25000,
    returnPercentage: 25.0,
    currency: 'USD'
  },
  revolutionaryFeatures = {
    aiPersonasUnlocked: 5,
    gamificationLevel: 12,
    socialFollowers: 1250,
    tradingStreak: 15,
    oracleAccuracy: 87.5
  }
}) => {
  const getTierColor = (tier: string) => {
    const colors = {
      rookie: '#9e9e9e',
      trader: '#4caf50',
      expert: '#2196f3',
      master: '#9c27b0',
      legend: '#ff9800',
      oracle: '#f44336'
    };
    return colors[tier as keyof typeof colors] || '#2196f3';
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'oracle': return '🔮';
      case 'legend': return '👑';
      case 'master': return '⭐';
      case 'expert': return '💎';
      case 'trader': return '📈';
      default: return '🌱';
    }
  };

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
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ mb: 1, color: '#fff', fontWeight: 600 }}>
            NeuroForge™ Personal Dashboard
          </Typography>
          <Typography variant="h6" sx={{ color: '#00d4ff', fontStyle: 'italic', mb: 2 }}>
            "Your Revolutionary Trading Command Center"
          </Typography>

          {/* User Profile Card */}
          <Card sx={{ 
            background: 'rgba(26, 26, 26, 0.95)',
            border: `2px solid ${getTierColor(user.tier || 'trader')}`,
            borderRadius: 3,
            mb: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar 
                  sx={{ 
                    width: 80, 
                    height: 80, 
                    border: `3px solid ${getTierColor(user.tier || 'trader')}`,
                    mr: 3,
                    fontSize: '2rem'
                  }}
                >
                  {getTierIcon(user.tier || 'trader')}
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5" sx={{ color: '#fff', fontWeight: 600, mb: 0.5 }}>
                    {user.name}
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#888', mb: 1 }}>
                    {user.email}
                  </Typography>
                  <Chip 
                    label={`${(user.tier || 'trader').toUpperCase()} TRADER`}
                    sx={{ 
                      bgcolor: getTierColor(user.tier || 'trader'),
                      color: '#fff',
                      fontWeight: 'bold',
                      fontSize: '0.8rem'
                    }}
                  />
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" sx={{ color: '#888' }}>
                    Member Since
                  </Typography>
                  <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
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
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 3,
              height: '100%'
            }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#fff', mb: 3, fontWeight: 600 }}>
                  💰 Portfolio Performance
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Total Value
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                        ${portfolio.totalValue.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Total Return
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 600 }}>
                        +${portfolio.totalReturn.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Return %
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 600 }}>
                        +{portfolio.returnPercentage.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: '#888', mb: 1 }}>
                        Invested
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#fff', fontWeight: 600 }}>
                        ${portfolio.totalInvested.toLocaleString()}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(100, portfolio.returnPercentage * 2)}
                  sx={{ 
                    mt: 3,
                    height: 12,
                    borderRadius: 6,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: 'linear-gradient(45deg, #4caf50, #8bc34a)',
                      borderRadius: 6
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 107, 53, 0.3)',
              borderRadius: 3,
              height: '100%'
            }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#fff', mb: 3, fontWeight: 600 }}>
                  🎯 Quick Actions
                </Typography>
                
                <Stack spacing={2}>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<TrendingUp />}
                    sx={{
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      color: '#000',
                      fontWeight: 600,
                      '&:hover': {
                        background: 'linear-gradient(45deg, #00b8e6, #0088bb)'
                      }
                    }}
                  >
                    Start Trading
                  </Button>
                  
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<SmartToy />}
                    sx={{
                      borderColor: '#ff6b35',
                      color: '#ff6b35',
                      '&:hover': {
                        bgcolor: 'rgba(255, 107, 53, 0.1)'
                      }
                    }}
                  >
                    AI Assistant
                  </Button>
                  
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<Assessment />}
                    sx={{
                      borderColor: '#4caf50',
                      color: '#4caf50',
                      '&:hover': {
                        bgcolor: 'rgba(76, 175, 80, 0.1)'
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

        {/* Revolutionary Features Showcase */}
        <Typography variant="h5" sx={{ mb: 3, color: '#fff', fontWeight: 600 }}>
          🚀 Revolutionary Features Status
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 3,
              '&:hover': {
                borderColor: 'rgba(0, 212, 255, 0.6)',
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SmartToy sx={{ color: '#00d4ff', fontSize: 32, mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    AI Personas
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
                  Unlocked trading personalities
                </Typography>
                <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                  {revolutionaryFeatures.aiPersonasUnlocked}/7
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(revolutionaryFeatures.aiPersonasUnlocked / 7) * 100}
                  sx={{ 
                    mt: 2,
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: '#00d4ff',
                      borderRadius: 4
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 107, 53, 0.3)',
              borderRadius: 3,
              '&:hover': {
                borderColor: 'rgba(255, 107, 53, 0.6)',
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <EmojiEvents sx={{ color: '#ff6b35', fontSize: 32, mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Gamification
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
                  Current level & achievements
                </Typography>
                <Typography variant="h4" sx={{ color: '#ff6b35', fontWeight: 600 }}>
                  Level {revolutionaryFeatures.gamificationLevel}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(revolutionaryFeatures.gamificationLevel / 50) * 100}
                  sx={{ 
                    mt: 2,
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: '#ff6b35',
                      borderRadius: 4
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <Card sx={{ 
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(76, 175, 80, 0.3)',
              borderRadius: 3,
              '&:hover': {
                borderColor: 'rgba(76, 175, 80, 0.6)',
                transform: 'translateY(-2px)',
                transition: 'all 0.3s ease'
              }
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Psychology sx={{ color: '#4caf50', fontSize: 32, mr: 2 }} />
                  <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                    Oracle Accuracy
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
                  Market prediction success rate
                </Typography>
                <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 600 }}>
                  {revolutionaryFeatures.oracleAccuracy.toFixed(1)}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={revolutionaryFeatures.oracleAccuracy}
                  sx={{ 
                    mt: 2,
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: '#4caf50',
                      borderRadius: 4
                    }
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Broker Account Manager */}
        <Card sx={{ 
          background: 'rgba(26, 26, 26, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 3
        }}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ color: '#fff', mb: 3, fontWeight: 600 }}>
              🏦 Broker Account Management
            </Typography>
            <BrokerAccountManager />
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default EnterpriseUserDashboard;
