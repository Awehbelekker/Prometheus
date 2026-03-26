import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Fade,
  Grow
} from '@mui/material';
import {
  Psychology,
  Security,
  Speed,
  Analytics,
  AccountBalance,
  ArrowForward,
  BarChart
} from '@mui/icons-material';
import ParticleBackground from './ParticleBackground';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [fadeIn, setFadeIn] = useState(false);

  useEffect(() => {
    setFadeIn(true);
  }, []);

  const features = [
    {
      icon: <Psychology sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'AI-Powered Trading',
      description: 'Advanced AI algorithms analyze market patterns and execute trades with precision.'
    },
    {
      icon: <Analytics sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'Real-Time Analytics',
      description: 'Live market data, portfolio tracking, and comprehensive performance metrics.'
    },
    {
      icon: <AccountBalance sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'Multi-Broker Support',
      description: 'Connect to Alpaca, Interactive Brokers, and more from a single platform.'
    },
    {
      icon: <Security sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'Risk Management',
      description: 'Built-in risk controls, position limits, and automated stop-loss protection.'
    },
    {
      icon: <Speed sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'Lightning Fast',
      description: 'Ultra-low latency execution with real-time market data streaming.'
    },
    {
      icon: <BarChart sx={{ fontSize: 48, color: '#00d4ff' }} />,
      title: 'Paper Trading',
      description: 'Practice strategies risk-free with our advanced paper trading simulator.'
    }
  ];

  const stats = [
    { label: 'Active Users', value: '10,000+', suffix: '' },
    { label: 'Trades Executed', value: '1M+', suffix: '' },
    { label: 'Success Rate', value: '87', suffix: '%' },
    { label: 'Uptime', value: '99.9', suffix: '%' }
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
          zIndex: 1
        }
      }}
    >
      {/* Particle Background */}
      <ParticleBackground
        particleCount={100}
        colors={['#00d4ff', '#0099cc', '#4caf50', '#ffffff']}
        speed={0.5}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
        {/* Hero Section */}
        <Fade in={fadeIn} timeout={1000}>
          <Box
            sx={{
              pt: { xs: 8, md: 12 },
              pb: { xs: 6, md: 8 },
              textAlign: 'center'
            }}
          >
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '4rem' },
                fontWeight: 800,
                background: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
                animation: 'fadeInUp 0.8s ease-out',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(30px)' },
                  to: { opacity: 1, transform: 'translateY(0)' }
                }
              }}
            >
              PROMETHEUS
            </Typography>
            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '1.5rem', md: '2.5rem' },
                fontWeight: 600,
                color: 'white',
                mb: 3,
                animation: 'fadeInUp 0.8s ease-out 0.2s both',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(30px)' },
                  to: { opacity: 1, transform: 'translateY(0)' }
                }
              }}
            >
              Ultimate AI Trading Platform
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                mb: 4,
                maxWidth: '700px',
                mx: 'auto',
                animation: 'fadeInUp 0.8s ease-out 0.4s both',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(30px)' },
                  to: { opacity: 1, transform: 'translateY(0)' }
                }
              }}
            >
              Trade smarter with AI-powered algorithms, real-time analytics, and multi-broker support.
              Join thousands of traders already using PROMETHEUS.
            </Typography>
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                justifyContent: 'center',
                flexWrap: 'wrap',
                animation: 'fadeInUp 0.8s ease-out 0.6s both',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(30px)' },
                  to: { opacity: 1, transform: 'translateY(0)' }
                }
              }}
            >
              <Button
                variant="contained"
                size="large"
                endIcon={<ArrowForward />}
                onClick={() => navigate('/login')}
                sx={{
                  background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  textTransform: 'none',
                  boxShadow: '0 8px 24px rgba(0, 212, 255, 0.3)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #0099cc, #007aa3)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 12px 32px rgba(0, 212, 255, 0.4)'
                  }
                }}
              >
                Get Started
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: '#00d4ff',
                  color: '#00d4ff',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  textTransform: 'none',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                Learn More
              </Button>
            </Box>
          </Box>
        </Fade>

        {/* Stats Section */}
        <Fade in={fadeIn} timeout={1500}>
          <Grid container spacing={3} sx={{ mb: 8, mt: 4 }}>
            {stats.map((stat, index) => (
              <Grid item xs={6} md={3} key={index}>
                <Grow in={fadeIn} timeout={1500 + index * 200}>
                  <Card
                    sx={{
                      background: 'rgba(0, 212, 255, 0.05)',
                      border: '1px solid rgba(0, 212, 255, 0.2)',
                      borderRadius: 2,
                      textAlign: 'center',
                      py: 3,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: 'rgba(0, 212, 255, 0.1)',
                        borderColor: 'rgba(0, 212, 255, 0.4)',
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 24px rgba(0, 212, 255, 0.2)'
                      }
                    }}
                  >
                    <CardContent>
                      <Typography
                        variant="h3"
                        sx={{
                          fontWeight: 700,
                          color: '#00d4ff',
                          mb: 1
                        }}
                      >
                        {stat.value}{stat.suffix}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          color: 'rgba(255, 255, 255, 0.7)',
                          textTransform: 'uppercase',
                          letterSpacing: 1
                        }}
                      >
                        {stat.label}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Fade>

        {/* Features Section */}
        <Box sx={{ mb: 8 }}>
          <Typography
            variant="h3"
            sx={{
              textAlign: 'center',
              fontWeight: 700,
              color: 'white',
              mb: 6,
              fontSize: { xs: '2rem', md: '2.5rem' }
            }}
          >
            Powerful Features
          </Typography>
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Grow in={fadeIn} timeout={2000 + index * 100}>
                  <Card
                    sx={{
                      height: '100%',
                      background: 'rgba(26, 26, 46, 0.8)',
                      border: '1px solid rgba(0, 212, 255, 0.2)',
                      borderRadius: 3,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'rgba(0, 212, 255, 0.5)',
                        transform: 'translateY(-8px)',
                        boxShadow: '0 12px 32px rgba(0, 212, 255, 0.2)',
                        background: 'rgba(26, 26, 46, 0.95)'
                      }
                    }}
                  >
                    <CardContent sx={{ p: 4, textAlign: 'center' }}>
                      <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 600,
                          color: 'white',
                          mb: 2
                        }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: 'rgba(255, 255, 255, 0.7)',
                          lineHeight: 1.7
                        }}
                      >
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grow>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* CTA Section */}
        <Fade in={fadeIn} timeout={2500}>
          <Box
            sx={{
              background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 4,
              p: { xs: 4, md: 6 },
              textAlign: 'center',
              mb: 8
            }}
          >
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                color: 'white',
                mb: 2
              }}
            >
              Ready to Start Trading?
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                mb: 4,
                maxWidth: '600px',
                mx: 'auto'
              }}
            >
              Join thousands of traders using PROMETHEUS to make smarter trading decisions.
            </Typography>
            <Button
              variant="contained"
              size="large"
              endIcon={<ArrowForward />}
              onClick={() => navigate('/login')}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                color: 'white',
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 600,
                borderRadius: 2,
                textTransform: 'none',
                boxShadow: '0 8px 24px rgba(0, 212, 255, 0.3)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  background: 'linear-gradient(45deg, #0099cc, #007aa3)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 32px rgba(0, 212, 255, 0.4)'
                }
              }}
            >
              Get Started Now
            </Button>
          </Box>
        </Fade>

        {/* Footer */}
        <Box
          sx={{
            borderTop: '1px solid rgba(0, 212, 255, 0.2)',
            pt: 4,
            pb: 4,
            textAlign: 'center'
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255, 255, 255, 0.5)'
            }}
          >
            © 2025 PROMETHEUS Trading Platform. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default LandingPage;
