import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  AdminPanelSettings as AdminIcon,
  TrendingUp as TradingIcon,
  Assessment as AnalyticsIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import NavigationButton from './NavigationButton';

interface MobileNavigationProps {
  user?: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  onLogout?: () => void;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  path: string;
  adminOnly?: boolean;
}

/**
 * Mobile Navigation Component
 * 
 * Provides responsive navigation with hamburger menu for mobile devices
 */
const MobileNavigation: React.FC<MobileNavigationProps> = ({
  user,
  onLogout
}) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const navigationItems: NavigationItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: DashboardIcon,
      path: '/dashboard'
    },
    {
      id: 'trading',
      label: 'Paper Trading',
      icon: TradingIcon,
      path: '/paper-trading'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: AnalyticsIcon,
      path: '/analytics'
    },
    {
      id: 'admin',
      label: 'Admin Cockpit',
      icon: AdminIcon,
      path: '/cockpit',
      adminOnly: true
    }
  ];

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
    setDrawerOpen(false);
  };

  const filteredItems = navigationItems.filter(item => 
    !item.adminOnly || (user?.role === 'admin')
  );

  // Don't render on desktop
  if (!isMobile) {
    return null;
  }

  const drawerContent = (
    <Box
      sx={{
        width: 280,
        height: '100%',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        color: 'white'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 3,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box>
          <Typography
            variant="h6"
            sx={{
              color: '#00d4ff',
              fontWeight: 700,
              mb: 0.5
            }}
          >
            PROMETHEUS
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: '#999',
              textTransform: 'uppercase',
              letterSpacing: 1
            }}
          >
            Trading Platform
          </Typography>
        </Box>
        <IconButton
          onClick={handleDrawerToggle}
          sx={{
            color: '#00d4ff',
            '&:hover': {
              backgroundColor: 'rgba(0, 212, 255, 0.1)'
            }
          }}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      {/* User Info */}
      {user && (
        <Box
          sx={{
            p: 3,
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: 'linear-gradient(45deg, #00d4ff, #9c27b0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 700
              }}
            >
              {user.name.charAt(0).toUpperCase()}
            </Box>
            <Box>
              <Typography
                variant="body2"
                sx={{
                  color: 'white',
                  fontWeight: 600
                }}
              >
                {user.name}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#999'
                }}
              >
                {user.role === 'admin' ? 'Administrator' : 'Trader'}
              </Typography>
            </Box>
          </Box>
        </Box>
      )}

      {/* Navigation Items */}
      <List sx={{ py: 2 }}>
        {filteredItems.map((item) => (
          <ListItem
            key={item.id}
            onClick={() => handleNavigation(item.path)}
            sx={{
              cursor: 'pointer',
              mx: 2,
              mb: 1,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                '& .MuiListItemIcon-root': {
                  color: '#00d4ff'
                },
                '& .MuiListItemText-primary': {
                  color: '#00d4ff'
                }
              }
            }}
          >
            <ListItemIcon
              sx={{
                color: '#999',
                minWidth: 40,
                transition: 'color 0.2s ease'
              }}
            >
              <item.icon />
            </ListItemIcon>
            <ListItemText
              primary={item.label}
              sx={{
                '& .MuiListItemText-primary': {
                  color: '#ccc',
                  fontWeight: 500,
                  transition: 'color 0.2s ease'
                }
              }}
            />
          </ListItem>
        ))}
      </List>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mx: 2 }} />

      {/* Settings and Logout */}
      <List sx={{ py: 2 }}>
        <ListItem
          onClick={() => handleNavigation('/settings')}
          sx={{
            cursor: 'pointer',
            mx: 2,
            mb: 1,
            borderRadius: 2,
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.05)'
            }
          }}
        >
          <ListItemIcon sx={{ color: '#999', minWidth: 40 }}>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText
            primary="Settings"
            sx={{
              '& .MuiListItemText-primary': {
                color: '#ccc',
                fontWeight: 500
              }
            }}
          />
        </ListItem>

        {onLogout && (
          <ListItem
            onClick={handleLogout}
            sx={{
              cursor: 'pointer',
              mx: 2,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                '& .MuiListItemIcon-root': {
                  color: '#f44336'
                },
                '& .MuiListItemText-primary': {
                  color: '#f44336'
                }
              }
            }}
          >
            <ListItemIcon sx={{ color: '#999', minWidth: 40 }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText
              primary="Logout"
              sx={{
                '& .MuiListItemText-primary': {
                  color: '#ccc',
                  fontWeight: 500
                }
              }}
            />
          </ListItem>
        )}
      </List>
    </Box>
  );

  return (
    <>
      {/* Mobile Header with Menu Button */}
      <Box
        className="mobile-nav"
        sx={{
          display: { xs: 'flex', md: 'none' },
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 2,
          background: 'rgba(26, 26, 26, 0.9)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          position: 'sticky',
          top: 0,
          zIndex: 1000
        }}
      >
        <IconButton
          className="mobile-menu-button"
          onClick={handleDrawerToggle}
          sx={{
            color: '#00d4ff',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 2,
            '&:hover': {
              backgroundColor: 'rgba(0, 212, 255, 0.1)'
            }
          }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          sx={{
            color: '#00d4ff',
            fontWeight: 700
          }}
        >
          PROMETHEUS
        </Typography>

        <Box sx={{ width: 48 }} /> {/* Spacer for centering */}
      </Box>

      {/* Mobile Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
            border: 'none'
          }
        }}
      >
        {drawerContent}
      </Drawer>
    </>
  );
};

export default MobileNavigation;
