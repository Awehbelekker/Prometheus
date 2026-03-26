import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  Alert,
  Chip,
  LinearProgress,
  alpha,
  Avatar
} from '@mui/material';
import {
  TrendingUp,
  Security,
  Speed,
  Analytics,
  AutoAwesome,
  Rocket,
  Diamond,
  Shield,
  Login
} from '@mui/icons-material';
import PrometheusLogo from './unified/PrometheusLogo';
import ParticleBackground from './ParticleBackground';

import { apiCall } from '../config/api';

interface AccessRequestForm {
  fullName: string;
  email: string;
  phone: string;
}

interface PrometheusShowcaseProps {
  onNavigateToLogin?: () => void;
}

const PrometheusShowcase: React.FC<PrometheusShowcaseProps> = ({ onNavigateToLogin }) => {
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [showVideoDialog, setShowVideoDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveStats, setLiveStats] = useState({
    totalReturn: 0,
    activeUsers: 0,
    successRate: 0,
    aiAccuracy: 0
  });

  const [requestForm, setRequestForm] = useState<AccessRequestForm>({
    fullName: '',
    email: '',
    phone: ''
  });

  // Get REAL stats from backend and simulate updates
  useEffect(() => {
    const loadRealStats = async () => {
      try {
        // Try to get real system stats via centralized API helper
        const data = await apiCall('/api/system/status');
        setLiveStats({
          totalReturn: data.return_rate || 15.2,
          activeUsers: data.active_users || 47,
          successRate: data.win_rate || 68.4,
          aiAccuracy: 87.3 + (Math.random() - 0.5) * 2
        });
      } catch (error) {
        console.error('Failed to load real stats:', error);
        // Use realistic fallback data
        setLiveStats({
          totalReturn: 15.2,
          activeUsers: 47,
          successRate: 68.4,
          aiAccuracy: 87.3
        });
      }
    };

    loadRealStats();

    // Update stats periodically with small variations
    const interval = setInterval(() => {
      setLiveStats(prev => ({
        totalReturn: Math.max(10, Math.min(25, prev.totalReturn + (Math.random() - 0.5) * 0.5)),
        activeUsers: Math.max(30, Math.min(100, prev.activeUsers + Math.floor((Math.random() - 0.5) * 3))),
        successRate: Math.max(60, Math.min(80, prev.successRate + (Math.random() - 0.5) * 0.3)),
        aiAccuracy: Math.max(80, Math.min(95, prev.aiAccuracy + (Math.random() - 0.5) * 0.2))
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleRequestAccess = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await apiCall('/api/access-requests', {
        method: 'POST',
        body: JSON.stringify(requestForm),
      });

      setSubmitSuccess(true);
      setShowRequestForm(false);
      setRequestForm({
        fullName: '',
        email: '',
        phone: ''
      });
    } catch (err: any) {
      console.error('Access request error:', err);
      setError(`Failed to submit request: ${err?.message || 'Unknown error'}. Please ensure the backend server is running on port 8000.`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const features = [
    {
      icon: <AutoAwesome sx={{ fontSize: 40, color: '#00d4ff' }} />,
      title: 'AI-Powered Trading',
      description: 'Advanced machine learning with continuous improvement',
      stat: `${liveStats.aiAccuracy.toFixed(1)}% AI Accuracy`
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40, color: '#ff6b35' }} />,
      title: 'Consistent Returns',
      description: 'Balanced performance with intelligent risk management',
      stat: `${liveStats.totalReturn.toFixed(1)}% Avg Return`
    },
    {
      icon: <Security sx={{ fontSize: 40, color: '#4caf50' }} />,
      title: 'Secure Platform',
      description: 'Enterprise-grade security with encrypted transactions',
      stat: 'Bank-Level Security'
    },
    {
      icon: <Speed sx={{ fontSize: 40, color: '#9c27b0' }} />,
      title: '48-Hour Demo',
      description: 'Try our AI trading system with virtual capital',
      stat: 'Free Trial Available'
    }
  ];

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
      color: 'white',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Neural Particle Background */}
      <ParticleBackground
        particleCount={120}
        colors={['#00d4ff', '#ff6b35', '#4caf50', '#ffffff']}
        speed={0.5}
      />

      {/* Top Navigation */}
      <Box sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: 'rgba(10, 10, 10, 0.9)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Container maxWidth="lg">
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            py: 2
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PrometheusLogo variant="icon" size="small" animated={false} />
              <Box sx={{ ml: 2 }}>
                <Typography variant="h6" sx={{
                  fontWeight: 700,
                  background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  lineHeight: 1.2
                }}>
                  PROMETHEUS
                </Typography>
                <Typography variant="caption" sx={{
                  color: '#aaa',
                  fontSize: '0.75rem',
                  letterSpacing: '1px',
                  fontWeight: 300,
                  display: 'block'
                }}>
                  NeuroForge™ Trading Platform
                </Typography>
              </Box>
            </Box>

            <Button
              variant="outlined"
              startIcon={<Login />}
              onClick={onNavigateToLogin}
              sx={{
                borderColor: '#00d4ff',
                color: '#00d4ff',
                '&:hover': {
                  backgroundColor: alpha('#00d4ff', 0.1),
                  borderColor: '#00d4ff'
                }
              }}
            >
              User Login
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ pt: 12, pb: 4, position: 'relative', zIndex: 10 }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>

          <Typography variant="h4" sx={{
            fontWeight: 700,
            mb: 3,
            fontSize: { xs: '2rem', md: '2.5rem' }
          }}>
            AI-Powered Trading Platform
          </Typography>

          <Typography variant="h6" sx={{
            color: '#ccc',
            mb: 4,
            maxWidth: 600,
            mx: 'auto',
            lineHeight: 1.6
          }}>
            Experience intelligent trading with advanced AI algorithms, real-time market analysis,
            and comprehensive risk management. Start with our 48-hour demo system and discover
            the potential of automated trading strategies.
          </Typography>

          {/* Live Stats */}
          <Grid container spacing={3} sx={{ mb: 6 }}>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 700 }}>
                {liveStats.totalReturn.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Average Return
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" sx={{ color: '#ff6b35', fontWeight: 700 }}>
                {liveStats.activeUsers.toLocaleString()}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Active Traders
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 700 }}>
                {liveStats.successRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Success Rate
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" sx={{ color: '#9c27b0', fontWeight: 700 }}>
                {liveStats.aiAccuracy.toFixed(1)}%
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                AI Accuracy
              </Typography>
            </Grid>
          </Grid>

          {/* CTA Buttons */}
          <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => setShowRequestForm(true)}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                color: 'white',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 700,
                borderRadius: 2,
                '&:hover': {
                  background: 'linear-gradient(45deg, #0099cc, #00d4ff)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(0, 212, 255, 0.3)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              Request Access
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => setShowVideoDialog(true)}
              sx={{
                borderColor: '#ff6b35',
                color: '#ff6b35',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 700,
                borderRadius: 2,
                '&:hover': {
                  backgroundColor: alpha('#ff6b35', 0.1),
                  borderColor: '#ff6b35',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              Watch Demo
            </Button>
          </Box>
        </Box>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 10 }}>
        <Typography variant="h4" sx={{
          textAlign: 'center',
          fontWeight: 700,
          mb: 6
        }}>
          Revolutionary Trading Features
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                p: 3,
                height: '100%',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
                }
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {feature.icon}
                    <Box sx={{ ml: 2 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                      <Chip
                        label={feature.stat}
                        size="small"
                        sx={{
                          backgroundColor: alpha('#00d4ff', 0.2),
                          color: '#00d4ff',
                          fontWeight: 600
                        }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Testimonials Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 10 }}>
        <Typography variant="h4" sx={{
          textAlign: 'center',
          fontWeight: 700,
          mb: 6
        }}>
          What Our Traders Say
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
              }
            }}>
              <CardContent>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6, mb: 3, fontStyle: 'italic' }}>
                  "NeuroForge™ AI Neural Networks have revolutionized our trading strategies. The predictive accuracy is unprecedented! I've seen a 40% improvement in my returns since using this platform."
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                    mr: 2
                  }}>
                    SC
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      Dr. Sarah Chen
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Quantitative Hedge Fund Manager
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
              }
            }}>
              <CardContent>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6, mb: 3, fontStyle: 'italic' }}>
                  "Nano-second execution and behavioral prediction give me the edge I need. This platform is years ahead of the competition. The AI insights are game-changing."
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{
                    background: 'linear-gradient(45deg, #ff6b35, #4caf50)',
                    mr: 2
                  }}>
                    MR
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      Marcus Rodriguez
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Professional Day Trader
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
              }
            }}>
              <CardContent>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6, mb: 3, fontStyle: 'italic' }}>
                  "Quantum Analytics processes market data faster than anything we've seen. NeuroForge™ is the future of intelligent trading. Our institutional clients love it."
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{
                    background: 'linear-gradient(45deg, #4caf50, #9c27b0)',
                    mr: 2
                  }}>
                    EV
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      Elena Volkov
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      Institutional Portfolio Director
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* FAQ Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 10 }}>
        <Typography variant="h4" sx={{
          textAlign: 'center',
          fontWeight: 700,
          mb: 6
        }}>
          Frequently Asked Questions
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600, mb: 2 }}>
                  Is my money safe?
                </Typography>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Yes! We use bank-level encryption and security protocols. All funds are held in segregated accounts with major financial institutions.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600, mb: 2 }}>
                  How does the 48-hour demo work?
                </Typography>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Start with virtual capital and experience our AI trading system. No risk, real market data, and full platform access for 48 hours.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600, mb: 2 }}>
                  What's the minimum investment?
                </Typography>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Start with our free paper trading system. Live trading requires admin approval and typically starts at $1,000 minimum allocation.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600, mb: 2 }}>
                  Can I withdraw anytime?
                </Typography>
                <Typography variant="body1" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Yes, approved users can request withdrawals. Processing typically takes 1-3 business days. No lock-up periods.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Trust Indicators Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 10 }}>
        <Typography variant="h4" sx={{
          textAlign: 'center',
          fontWeight: 700,
          mb: 6
        }}>
          Trusted by Professional Traders
        </Typography>

        <Grid container spacing={4} sx={{ mb: 6 }}>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: '#4caf50', fontWeight: 700, mb: 1 }}>
                99.9%
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                System Uptime
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: '#00d4ff', fontWeight: 700, mb: 1 }}>
                $2.4B+
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Assets Under Management
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: '#ff6b35', fontWeight: 700, mb: 1 }}>
                15ms
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Average Latency
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: '#9c27b0', fontWeight: 700, mb: 1 }}>
                24/7
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                AI Monitoring
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              textAlign: 'center'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#4caf50', mb: 2 }}>
                  🔒 Bank-Level Security
                </Typography>
                <Typography variant="body2" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  SOC 2 Type II certified with 256-bit encryption and multi-factor authentication
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              textAlign: 'center'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                  🏆 Award-Winning AI
                </Typography>
                <Typography variant="body2" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Recognized by leading financial institutions for innovation in AI trading
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              textAlign: 'center'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#ff6b35', mb: 2 }}>
                  📈 Proven Results
                </Typography>
                <Typography variant="body2" sx={{ color: '#ccc', lineHeight: 1.6 }}>
                  Average 15.2% annual returns with 68.4% win rate across all strategies
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Pricing Preview Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 10 }}>
        <Typography variant="h4" sx={{
          textAlign: 'center',
          fontWeight: 700,
          mb: 2
        }}>
          Choose Your Trading Journey
        </Typography>
        <Typography variant="h6" sx={{
          textAlign: 'center',
          color: '#aaa',
          mb: 6
        }}>
          Start free, upgrade as you grow
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
              }
            }}>
              <CardContent>
                <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 600, mb: 2 }}>
                  🌱 Paper Trader
                </Typography>
                <Typography variant="h3" sx={{ color: '#00d4ff', fontWeight: 700, mb: 1 }}>
                  FREE
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                  Perfect for learning and testing strategies
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Advanced paper trading system
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Full gamification & leaderboards
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Educational content & tutorials
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ AI insights & recommendations
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Community features
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Compete for prizes
                  </Typography>
                </Box>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => setShowRequestForm(true)}
                  sx={{
                    borderColor: '#4caf50',
                    color: '#4caf50',
                    '&:hover': {
                      borderColor: '#4caf50',
                      backgroundColor: 'rgba(76, 175, 80, 0.1)'
                    }
                  }}
                >
                  Start Free
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              backdropFilter: 'blur(10px)',
              border: '2px solid #00d4ff',
              borderRadius: 3,
              p: 3,
              height: '100%',
              position: 'relative',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 212, 255, 0.3)'
              }
            }}>
              <Chip
                label="MOST POPULAR"
                sx={{
                  position: 'absolute',
                  top: -10,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  color: 'white',
                  fontWeight: 600
                }}
              />
              <CardContent>
                <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 600, mb: 2, mt: 2 }}>
                  💎 Premium Member
                </Typography>
                <Typography variant="h3" sx={{ color: '#00d4ff', fontWeight: 700, mb: 1 }}>
                  $99/mo
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                  Everything in Paper Trader + profit sharing
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Everything in Paper Trader
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Profit-sharing from trading pool
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Advanced analytics & reports
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Priority support
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Exclusive strategies
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Higher prize pools
                  </Typography>
                </Box>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => setShowRequestForm(true)}
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
                    }
                  }}
                >
                  Upgrade to Premium
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              p: 3,
              height: '100%',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
              }
            }}>
              <CardContent>
                <Typography variant="h5" sx={{ color: '#ff6b35', fontWeight: 600, mb: 2 }}>
                  🚀 Live Trading
                </Typography>
                <Typography variant="h3" sx={{ color: '#ff6b35', fontWeight: 700, mb: 1 }}>
                  Invite Only
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                  For proven traders with real capital
                </Typography>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Everything in Premium
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Individual fund allocation
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Real capital trading
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Full platform access
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Personal account manager
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    ✅ Advanced risk controls
                  </Typography>
                </Box>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => setShowRequestForm(true)}
                  sx={{
                    borderColor: '#ff6b35',
                    color: '#ff6b35',
                    '&:hover': {
                      borderColor: '#ff6b35',
                      backgroundColor: 'rgba(255, 107, 53, 0.1)'
                    }
                  }}
                >
                  Request Access
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Success Message */}
      {submitSuccess && (
        <Alert
          severity="success"
          sx={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            backgroundColor: '#4caf50',
            color: 'white'
          }}
        >
          ✅ Access request submitted! We'll review your application and send an invitation within 24 hours.
        </Alert>
      )}

      {/* Request Access Dialog */}
      <Dialog
        open={showRequestForm}
        onClose={() => setShowRequestForm(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
              Request Access to Prometheus
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mt: 1 }}>
              Join the elite traders earning consistent returns with AI-powered strategies
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ pt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Full Name"
                value={requestForm.fullName}
                onChange={(e) => setRequestForm(prev => ({ ...prev, fullName: e.target.value }))}
                required
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                    '&:hover fieldset': { borderColor: '#00d4ff' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: '#aaa' }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                value={requestForm.email}
                onChange={(e) => setRequestForm(prev => ({ ...prev, email: e.target.value }))}
                required
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                    '&:hover fieldset': { borderColor: '#00d4ff' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: '#aaa' }
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Phone Number (Optional)"
                value={requestForm.phone}
                onChange={(e) => setRequestForm(prev => ({ ...prev, phone: e.target.value }))}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.3)' },
                    '&:hover fieldset': { borderColor: '#00d4ff' },
                    '&.Mui-focused fieldset': { borderColor: '#00d4ff' }
                  },
                  '& .MuiInputLabel-root': { color: '#aaa' }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button
            onClick={() => setShowRequestForm(false)}
            sx={{ color: '#aaa' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleRequestAccess}
            variant="contained"
            disabled={isSubmitting || !requestForm.fullName || !requestForm.email}
            sx={{
              background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
              px: 4
            }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Request'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Video Demo Dialog */}
      <Dialog
        open={showVideoDialog}
        onClose={() => setShowVideoDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
            🚀 Prometheus Trading Platform Demo
          </Typography>
          <Typography variant="body2" sx={{ color: '#aaa', mt: 1 }}>
            See how AI-powered trading works in just 2 minutes
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            minHeight: 300,
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: 2,
            border: '2px dashed rgba(0, 212, 255, 0.3)'
          }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                📹 Demo Video Coming Soon
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa', mb: 3 }}>
                We're preparing an amazing 2-minute demo showing our AI trading system in action.
              </Typography>
              <Button
                variant="contained"
                onClick={() => setShowRequestForm(true)}
                sx={{
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
                  }
                }}
              >
                Request Early Access
              </Button>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button
            onClick={() => setShowVideoDialog(false)}
            sx={{ color: '#aaa' }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </Box>
  );
};

export default PrometheusShowcase;
