import React from 'react';
import { Box, Typography, Chip, alpha, Button } from '@mui/material';
import Logo from '../Logo';

/**
 * 🎯 MINIMAL PROFESSIONAL HEADER
 * Clean, simple header with original logo
 */

interface MinimalHeaderProps {
  user: {
    username: string;
    email: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  onLogout?: () => void;
}

const MinimalHeader: React.FC<MinimalHeaderProps> = ({ user, onLogout }) => {
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
      background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.9) 0%, rgba(10, 10, 10, 0.95) 100%)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3,
      p: 3,
      mb: 4,
      backdropFilter: 'blur(10px)'
    }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between'
      }}>
        {/* Logo and Branding */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Logo size="medium" theme="dark" />
          <Box>
            <Typography variant="h4" sx={{
              fontWeight: 800,
              color: 'white',
              letterSpacing: '1px',
              mb: 0.5
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

        {/* User Info */}
        <Box sx={{ textAlign: 'right' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Typography variant="h6" sx={{
              color: 'white',
              fontWeight: 600
            }}>
              Welcome, {user.username}
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
          <Typography variant="body2" sx={{ 
            color: '#aaa',
            fontFamily: 'monospace'
          }}>
            {user.email}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default MinimalHeader;
