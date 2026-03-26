import React from 'react';
import { Box, Typography, Chip, alpha, Button, Avatar } from '@mui/material';
import { Person, Settings, ExitToApp } from '@mui/icons-material';
import PrometheusLogo from './PrometheusLogo';

/**
 * 🌟 HOLOGRAPHIC HEADER
 * Futuristic header with animated logo effects
 */

interface HolographicHeaderProps {
  user: {
    username: string;
    email: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  onLogout?: () => void;
}

const HolographicHeader: React.FC<HolographicHeaderProps> = ({ user, onLogout }) => {
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
      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(0, 212, 255, 0.3)',
      borderRadius: 3,
      p: 3,
      mb: 4,
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
      <Box sx={{
        position: 'absolute',
        top: -50,
        right: -50,
        width: 200,
        height: 200,
        background: 'radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        animation: 'float 6s ease-in-out infinite'
      }} />
      
      <Box sx={{
        position: 'absolute',
        bottom: -30,
        left: -30,
        width: 150,
        height: 150,
        background: 'radial-gradient(circle, rgba(255, 107, 53, 0.1) 0%, transparent 70%)',
        borderRadius: '50%',
        animation: 'float 8s ease-in-out infinite reverse'
      }} />

      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        position: 'relative',
        zIndex: 2
      }}>
        {/* Holographic Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <PrometheusLogo variant="full" size="large" animated={true} />
        </Box>

        {/* User Profile Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip 
            label={getTierLabel(user.tier)}
            sx={{ 
              backgroundColor: alpha(getTierColor(user.tier), 0.3),
              color: getTierColor(user.tier),
              fontWeight: 700,
              fontSize: '0.9rem',
              height: 32,
              border: `1px solid ${getTierColor(user.tier)}`
            }}
          />
          
          <Button
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              color: 'white',
              textTransform: 'none',
              backgroundColor: alpha('#00d4ff', 0.1),
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 2,
              px: 2,
              py: 1,
              '&:hover': {
                backgroundColor: alpha('#00d4ff', 0.2),
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0, 212, 255, 0.3)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            <Avatar sx={{ 
              width: 36, 
              height: 36, 
              background: 'linear-gradient(45deg, #00d4ff, #9c27b0)',
              fontWeight: 700
            }}>
              {user.username.charAt(0).toUpperCase()}
            </Avatar>
            <Box sx={{ textAlign: 'left' }}>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                {user.username}
              </Typography>
              <Typography variant="caption" sx={{ color: '#aaa' }}>
                {user.email}
              </Typography>
            </Box>
          </Button>
        </Box>
      </Box>
      
      {/* CSS Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
      `}</style>
    </Box>
  );
};

export default HolographicHeader;
