import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  useTheme,
  alpha,
  Tooltip
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle,
  ExitToApp,
  Person,
  Shield,
  TrendingUp,
  Speed,
  Security
} from '@mui/icons-material';
import Logo from './Logo';

interface TopNavigationProps {
  currentUser?: any;
  onLogout?: () => void;
  title?: string;
  showStats?: boolean;
}

const TopNavigation: React.FC<TopNavigationProps> = ({
  currentUser,
  onLogout,
  title = 'Dashboard',
  showStats = true
}) => {
  const theme = useTheme();
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState<null | HTMLElement>(null);

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleNotificationsClick = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleNotificationsClose = () => {
    setNotificationsAnchor(null);
  };

  const handleLogout = () => {
    handleProfileClose();

    // Clear all authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    sessionStorage.clear();

    // Call the logout function if provided
    if (onLogout) {
      onLogout();
    }

    // Force redirect to login page
    window.location.href = '/';
  };

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: alpha('#1a1a1a', 0.95),
        backdropFilter: 'blur(10px)',
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        zIndex: theme.zIndex.drawer - 1
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        {/* Logo and Brand Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Logo size="small" theme="dark" />
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: 'white',
              letterSpacing: '0.5px',
              background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            PROMETHEUS
          </Typography>
        </Box>
        {/* Left Section - Title and Stats */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              color: '#ffffff',
              fontSize: '1.5rem'
            }}
          >
            {title}
          </Typography>

          {showStats && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                icon={<TrendingUp sx={{ fontSize: '1rem' }} />}
                label="Live Trading Active"
                size="small"
                sx={{
                  backgroundColor: alpha('#4caf50', 0.2),
                  color: '#4caf50',
                  border: `1px solid ${alpha('#4caf50', 0.3)}`,
                  '& .MuiChip-icon': { color: '#4caf50' }
                }}
              />
              <Chip
                icon={<Speed sx={{ fontSize: '1rem' }} />}
                label="AI Learning"
                size="small"
                sx={{
                  backgroundColor: alpha('#ff9800', 0.2),
                  color: '#ff9800',
                  border: `1px solid ${alpha('#ff9800', 0.3)}`,
                  '& .MuiChip-icon': { color: '#ff9800' }
                }}
              />
              <Chip
                icon={<Security sx={{ fontSize: '1rem' }} />}
                label="Risk Protected"
                size="small"
                sx={{
                  backgroundColor: alpha('#2196f3', 0.2),
                  color: '#2196f3',
                  border: `1px solid ${alpha('#2196f3', 0.3)}`,
                  '& .MuiChip-icon': { color: '#2196f3' }
                }}
              />
            </Box>
          )}
        </Box>

        {/* Right Section - User Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton
              onClick={handleNotificationsClick}
              sx={{
                color: '#ffffff',
                '&:hover': { backgroundColor: alpha('#00d4ff', 0.1) }
              }}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Settings">
            <IconButton
              sx={{
                color: '#ffffff',
                '&:hover': { backgroundColor: alpha('#00d4ff', 0.1) }
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          {/* User Profile */}
          {currentUser && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, ml: 2 }}>
              <Box sx={{ textAlign: 'right', display: { xs: 'none', sm: 'block' } }}>
                <Typography
                  variant="subtitle2"
                  sx={{
                    color: '#ffffff',
                    fontWeight: 600,
                    lineHeight: 1.2
                  }}
                >
                  {currentUser.name || 'User'}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#b0b0b0',
                    textTransform: 'uppercase',
                    fontWeight: 500
                  }}
                >
                  {currentUser.role || 'User'}
                </Typography>
              </Box>

              <Tooltip title="Profile Menu">
                <IconButton
                  onClick={handleProfileClick}
                  sx={{
                    p: 0,
                    '&:hover': { transform: 'scale(1.05)' },
                    transition: 'transform 0.2s ease-in-out'
                  }}
                >
                  <Avatar
                    sx={{
                      width: 40,
                      height: 40,
                      backgroundColor: '#00d4ff',
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      border: `2px solid ${alpha('#00d4ff', 0.3)}`
                    }}
                  >
                    {currentUser.name?.charAt(0) || 'U'}
                  </Avatar>
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationsAnchor}
          open={Boolean(notificationsAnchor)}
          onClose={handleNotificationsClose}
          PaperProps={{
            sx: {
              backgroundColor: '#2a2a2a',
              border: `1px solid ${alpha('#00d4ff', 0.2)}`,
              minWidth: 300,
              maxHeight: 400
            }
          }}
        >
          <Box sx={{ p: 2, borderBottom: `1px solid ${alpha('#ffffff', 0.1)}` }}>
            <Typography variant="h6" sx={{ color: '#ffffff', fontWeight: 600 }}>
              Notifications
            </Typography>
          </Box>
          
          <MenuItem sx={{ color: '#ffffff', py: 2 }}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                🚀 New AI Strategy Deployed
              </Typography>
              <Typography variant="caption" sx={{ color: '#b0b0b0' }}>
                Quantum Neural strategy is now active - 2 min ago
              </Typography>
            </Box>
          </MenuItem>
          
          <MenuItem sx={{ color: '#ffffff', py: 2 }}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                💰 Trade Executed Successfully
              </Typography>
              <Typography variant="caption" sx={{ color: '#b0b0b0' }}>
                AAPL position closed with +$245 profit - 5 min ago
              </Typography>
            </Box>
          </MenuItem>
          
          <MenuItem sx={{ color: '#ffffff', py: 2 }}>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                ⚠️ Risk Alert Triggered
              </Typography>
              <Typography variant="caption" sx={{ color: '#b0b0b0' }}>
                Portfolio exposure exceeded 80% - 10 min ago
              </Typography>
            </Box>
          </MenuItem>
        </Menu>

        {/* Profile Menu */}
        <Menu
          anchorEl={profileMenuAnchor}
          open={Boolean(profileMenuAnchor)}
          onClose={handleProfileClose}
          PaperProps={{
            sx: {
              backgroundColor: '#2a2a2a',
              border: `1px solid ${alpha('#00d4ff', 0.2)}`,
              minWidth: 220
            }
          }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          <Box sx={{ p: 2, borderBottom: `1px solid ${alpha('#ffffff', 0.1)}` }}>
            <Typography variant="subtitle1" sx={{ color: '#ffffff', fontWeight: 600 }}>
              {currentUser?.name || 'User'}
            </Typography>
            <Typography variant="caption" sx={{ color: '#b0b0b0' }}>
              {currentUser?.email || 'user@example.com'}
            </Typography>
          </Box>
          
          <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff', py: 1.5 }}>
            <Person sx={{ mr: 2, color: '#00d4ff' }} />
            Profile
          </MenuItem>
          
          <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff', py: 1.5 }}>
            <SettingsIcon sx={{ mr: 2, color: '#00d4ff' }} />
            Settings
          </MenuItem>
          
          <MenuItem onClick={handleProfileClose} sx={{ color: '#ffffff', py: 1.5 }}>
            <Shield sx={{ mr: 2, color: '#00d4ff' }} />
            Security
          </MenuItem>
          
          <Divider sx={{ backgroundColor: alpha('#ffffff', 0.1) }} />
          
          <MenuItem onClick={handleLogout} sx={{ color: '#ff6b35', py: 1.5 }}>
            <ExitToApp sx={{ mr: 2 }} />
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavigation;
