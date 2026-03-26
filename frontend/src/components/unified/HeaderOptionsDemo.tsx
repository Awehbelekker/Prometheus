import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Divider } from '@mui/material';
import TradingCommandCenter from './TradingCommandCenter';
import HolographicHeader from './HolographicHeader';
import MinimalHeader from './MinimalHeader';

/**
 * 🎨 HEADER OPTIONS DEMO
 * Shows all 3 header options side by side for comparison
 */

const HeaderOptionsDemo: React.FC = () => {
  const demoUser = {
    username: 'DemoUser',
    email: 'demo@prometheus.com',
    tier: 'premium' as const
  };

  return (
    <Box sx={{ 
      p: 4, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      color: 'white'
    }}>
      <Typography variant="h3" sx={{ 
        mb: 4, 
        textAlign: 'center',
        fontWeight: 800,
        background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        🎯 Dashboard Header Options
      </Typography>

      <Typography variant="h6" sx={{ 
        mb: 6, 
        textAlign: 'center',
        color: '#aaa'
      }}>
        Choose the perfect header style for your Prometheus trading experience
      </Typography>

      <Grid container spacing={4}>
        {/* Option 1: Trading Command Center */}
        <Grid item xs={12}>
          <Card sx={{
            backgroundColor: 'rgba(26, 26, 46, 0.3)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: '#4caf50',
                  animation: 'pulse 2s infinite'
                }} />
                <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 700 }}>
                  Option 1: Trading Command Center (RECOMMENDED)
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ color: '#aaa', mb: 3 }}>
                Professional dashboard with live stats, original logo, and real-time monitoring. Perfect for serious traders.
              </Typography>
              <TradingCommandCenter user={demoUser} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 2 }} />
        </Grid>

        {/* Option 2: Holographic Header */}
        <Grid item xs={12}>
          <Card sx={{
            backgroundColor: 'rgba(26, 26, 46, 0.3)',
            border: '1px solid rgba(156, 39, 176, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: '#9c27b0',
                  animation: 'pulse 2s infinite'
                }} />
                <Typography variant="h5" sx={{ color: '#9c27b0', fontWeight: 700 }}>
                  Option 2: Holographic Header
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ color: '#aaa', mb: 3 }}>
                Futuristic header with animated logo effects and holographic elements. For users who love visual flair.
              </Typography>
              <HolographicHeader user={demoUser} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 2 }} />
        </Grid>

        {/* Option 3: Minimal Professional */}
        <Grid item xs={12}>
          <Card sx={{
            backgroundColor: 'rgba(26, 26, 46, 0.3)',
            border: '1px solid rgba(255, 152, 0, 0.3)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: '#ff9800',
                  animation: 'pulse 2s infinite'
                }} />
                <Typography variant="h5" sx={{ color: '#ff9800', fontWeight: 700 }}>
                  Option 3: Minimal Professional
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ color: '#aaa', mb: 3 }}>
                Clean, simple header with original logo and essential information only. Perfect for minimalist users.
              </Typography>
              <MinimalHeader user={demoUser} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Instructions */}
      <Box sx={{ 
        mt: 6, 
        p: 4, 
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 3,
        textAlign: 'center'
      }}>
        <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2, fontWeight: 700 }}>
          🎯 How to Switch Headers
        </Typography>
        <Typography variant="body1" sx={{ color: '#aaa' }}>
          In the dashboard, look for the <strong>Settings</strong> button in the top-right corner. 
          Click it to open the header selector and choose your preferred style instantly!
        </Typography>
      </Box>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </Box>
  );
};

export default HeaderOptionsDemo;
